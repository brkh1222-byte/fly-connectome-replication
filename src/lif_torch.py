"""Batched, event-driven PyTorch implementation of the Shiu et al. (2024) LIF model.

Reimplemented from the model equations and from the Brian2 semantics measured in
notes/brian2_semantics.md (not copied from any GPL code). Many trials run at once as rows of
a (B, N) state matrix.

Model (per neuron i, Shiu's parameters):
    tau_m dv/dt = (v_0 - v) + g        (frozen while refractory)
    tau_g dg/dt = -g                   (frozen while refractory)
    spike if v > v_th and not refractory -> v = v_rst, g = 0, refractory for t_rfc
    presynaptic spike of j at step s -> g_i += w_ji at step s + d (d = t_dly/dt), but only if
    neuron i is not refractory at that step (Brian2 discards it otherwise)
    Poisson-driven neurons: Bernoulli(rate*dt) kicks of w_syn*f_poi on v each step and no
    refractory period (Shiu sets rfc = 0 for them)

Integration is exact for the linear ODE (Brian2 method='linear'), dt = 0.1 ms. The order of
operations inside one step follows Brian2's schedule: groups -> thresholds -> synapses -> resets.

Synaptic delivery is event-driven: the outgoing synapses of spiking neurons are gathered from
a CSR matrix (rows = presynaptic neurons) and scattered into g with index_add_. The cost is
proportional to the number of spikes, not to the number of synapses.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import torch


@dataclass
class LIFParams:
    v_0: float = -52.0      # mV resting potential
    v_rst: float = -52.0    # mV reset
    v_th: float = -45.0     # mV threshold
    t_mbr: float = 20.0     # ms membrane time constant
    tau: float = 5.0        # ms synaptic time constant
    t_rfc: float = 2.2      # ms refractory period
    t_dly: float = 1.8      # ms synaptic delay
    w_syn: float = 0.275    # mV per synapse (Shiu's single free parameter)
    f_poi: float = 250.0    # Poisson kick = w_syn * f_poi
    dt: float = 0.1         # ms
    t_run: float = 1000.0   # ms


class Network:
    """Holds the CSR connectivity on a device.

    pre, post: int arrays of edges; weight: signed synapse counts (or any real weight in units
    of synapses; multiplied by w_syn).
    """

    def __init__(self, n, pre, post, weight, params: LIFParams | None = None,
                 device="cpu", dtype=torch.float32):
        self.n = int(n)
        self.p = params or LIFParams()
        self.device = torch.device(device)
        self.dtype = dtype
        pre = np.asarray(pre, dtype=np.int64)
        post = np.asarray(post, dtype=np.int64)
        w = np.asarray(weight, dtype=np.float64) * self.p.w_syn
        order = np.argsort(pre, kind="stable")
        pre, post, w = pre[order], post[order], w[order]
        counts = np.bincount(pre, minlength=self.n)
        indptr = np.zeros(self.n + 1, dtype=np.int64)
        np.cumsum(counts, out=indptr[1:])
        self.indptr = torch.as_tensor(indptr, device=self.device)
        self.deg = torch.as_tensor(counts, device=self.device)
        self.indices = torch.as_tensor(post, device=self.device)
        self.data = torch.as_tensor(w, dtype=dtype, device=self.device)

    def silence(self, idx):
        """Shiu's silencing: zero all outgoing synapses of the given neurons (returns a copy
        of the weight vector so the network can be restored)."""
        old = self.data.clone()
        for i in np.atleast_1d(idx):
            a, b = int(self.indptr[i]), int(self.indptr[i + 1])
            self.data[a:b] = 0
        return old

    # ------------------------------------------------------------------
    def _deliver(self, sb, sj, g, not_ref_flat):
        """Scatter the outgoing weights of spikes (trial sb, neuron sj) into g (B, N)."""
        if sj.numel() == 0:
            return
        cnt = self.deg[sj]
        total = int(cnt.sum())
        if total == 0:
            return
        starts = self.indptr[sj]
        rep = torch.repeat_interleave(torch.arange(sj.numel(), device=self.device), cnt)
        first = torch.cumsum(cnt, 0) - cnt
        pos = starts[rep] + (torch.arange(total, device=self.device) - first[rep])
        tgt = sb[rep] * self.n + self.indices[pos]
        w = self.data[pos] * not_ref_flat[tgt]
        g.view(-1).index_add_(0, tgt, w)

    @torch.no_grad()
    def run(self, n_trials, stim, seed=0, t_run=None, record_spikes=False):
        """Simulate n_trials independent trials.

        stim: list of (indices, rate_Hz) groups driven by Poisson input.
        Returns counts (n_trials, N) int32 tensor on CPU, and optionally a list of
        (step, trial, neuron) spike arrays.
        """
        p = self.p
        dev, dt_, N, B = self.device, self.dtype, self.n, int(n_trials)
        T = int(round((t_run or p.t_run) / p.dt))
        d = int(round(p.t_dly / p.dt))
        rfc_steps = torch.full((N,), int(round(p.t_rfc / p.dt)), dtype=torch.int32, device=dev)
        gen = torch.Generator(device="cpu").manual_seed(int(seed))

        # exact propagators (Brian2 'linear')
        a_g = math.exp(-p.dt / p.tau)
        a_v = math.exp(-p.dt / p.t_mbr)
        k_vg = p.tau / (p.t_mbr - p.tau) * (math.exp(-p.dt / p.t_mbr) - math.exp(-p.dt / p.tau))

        v = torch.full((B, N), p.v_0, dtype=dt_, device=dev)
        g = torch.zeros((B, N), dtype=dt_, device=dev)
        last = torch.full((B, N), -10 ** 6, dtype=torch.int32, device=dev)
        counts = torch.zeros((B, N), dtype=torch.int32, device=dev)

        st_idx, st_p = [], []
        for idx, rate in stim:
            idx = torch.as_tensor(np.asarray(idx, dtype=np.int64), device=dev)
            if idx.numel() == 0:
                continue
            rfc_steps[idx] = 0
            st_idx.append(idx)
            st_p.append(float(rate) * p.dt * 1e-3)
        kick = p.w_syn * p.f_poi
        queue = [None] * d  # ring buffer of (sb, sj) spikes waiting to be delivered
        spikes_out = []

        for t in range(T):
            # 1) state update (groups slot) for non-refractory neurons
            not_ref = (t - last) >= rfc_steps
            g_new = g * a_g
            v_new = p.v_0 + (v - p.v_0) * a_v + k_vg * g
            v = torch.where(not_ref, v_new, v)
            g = torch.where(not_ref, g_new, g)
            # 2) threshold
            spk = (v > p.v_th) & not_ref
            sb, sj = torch.nonzero(spk, as_tuple=True)
            if sj.numel():
                last[sb, sj] = t
                not_ref[sb, sj] = False
                counts[sb, sj] += 1
                if record_spikes:
                    spikes_out.append((t, sb.cpu().numpy(), sj.cpu().numpy()))
            # 3) synapses: deliver spikes emitted d steps ago; Poisson kicks
            old = queue[t % d]
            if old is not None:
                self._deliver(old[0], old[1], g, not_ref.view(-1).to(dt_))
            queue[t % d] = (sb, sj)
            for idx, pr in zip(st_idx, st_p):
                hit = torch.rand((B, idx.numel()), generator=gen) < pr
                if hit.any():
                    hit = hit.to(dev)
                    v[:, idx] += kick * hit.to(dt_) * not_ref[:, idx].to(dt_)
            # 4) reset
            if sj.numel():
                v[sb, sj] = p.v_rst
                g[sb, sj] = 0.0
        out = counts.cpu()
        return (out, spikes_out) if record_spikes else out


def load_shiu(version="783", root=None):
    """Load Shiu's own model input files (completeness + connectivity) as arrays."""
    import pandas as pd
    from pathlib import Path
    root = Path(root or Path(__file__).resolve().parents[1] / "data" / "external" / "shiu_repo")
    files = {"630": ("2023_03_23_completeness_630_final.csv", "2023_03_23_connectivity_630_final.parquet"),
             "783": ("Completeness_783.csv", "Connectivity_783.parquet")}[version]
    comp = pd.read_csv(root / files[0], index_col=0)
    con = pd.read_parquet(root / files[1], columns=["Presynaptic_Index", "Postsynaptic_Index",
                                                    "Excitatory x Connectivity"])
    return (comp.index.values, con["Presynaptic_Index"].values, con["Postsynaptic_Index"].values,
            con["Excitatory x Connectivity"].values)
