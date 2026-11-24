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
        w = self.data[pos] * not_ref_flat[tgt].to(self.dtype)
        g.view(-1).index_add_(0, tgt, w)

    @torch.no_grad()
    def run(self, n_trials, stim, seed=0, t_run=None):
        """Simulate n_trials trials of one experiment. stim: list of (indices, rate_Hz).
        Returns counts (n_trials, N) int32 on CPU."""
        return self.run_batch([stim], n_trials, seed=seed, t_run=t_run)[0]

    @torch.no_grad()
    def run_batch(self, exps, n_trials, seed=0, t_run=None, return_device=False):
        """Simulate several experiments at once; each gets n_trials rows of the state matrix.

        exps: list of experiments; each experiment is a list of (indices, rate_Hz) groups
              driven by Poisson input (rfc = 0 for driven neurons in that experiment only).
        Returns counts (n_exp, n_trials, N) int32 (CPU unless return_device).
        """
        p = self.p
        dev, dt_, N = self.device, self.dtype, self.n
        E, R = len(exps), int(n_trials)
        B = E * R
        T = int(round((t_run or p.t_run) / p.dt))
        d = int(round(p.t_dly / p.dt))
        rfc_default = int(round(p.t_rfc / p.dt))

        # exact propagators (Brian2 'linear')
        a_g = math.exp(-p.dt / p.tau)
        a_v = math.exp(-p.dt / p.t_mbr)
        k_vg = p.tau / (p.t_mbr - p.tau) * (math.exp(-p.dt / p.t_mbr) - math.exp(-p.dt / p.tau))
        kick = p.w_syn * p.f_poi

        # union of driven neurons and per-row Bernoulli probabilities
        union = sorted({int(i) for ex in exps for idx, _ in ex for i in np.atleast_1d(idx)})
        U = len(union)
        col = {n_: k for k, n_ in enumerate(union)}
        prob = torch.zeros((B, max(U, 1)), dtype=torch.float32)
        rfc = torch.full((B, N), rfc_default, dtype=torch.int16)
        for e, ex in enumerate(exps):
            for idx, rate in ex:
                idx = np.atleast_1d(np.asarray(idx, dtype=np.int64))
                if idx.size == 0:
                    continue
                cols = [col[int(i)] for i in idx]
                prob[e * R:(e + 1) * R, cols] = float(rate) * p.dt * 1e-3
                rfc[e * R:(e + 1) * R, torch.as_tensor(idx)] = 0
        prob = prob.to(dev)
        rfc = rfc.to(dev)
        uidx = torch.as_tensor(union, dtype=torch.int64, device=dev)

        try:
            gen = torch.Generator(device=dev)
        except RuntimeError:
            gen = None
        if gen is not None:
            gen.manual_seed(int(seed))
            rand = lambda: torch.rand((B, max(U, 1)), generator=gen, device=dev)
        else:  # pragma: no cover - backends without device generators
            cg = torch.Generator().manual_seed(int(seed))
            rand = lambda: torch.rand((B, max(U, 1)), generator=cg).to(dev)

        v = torch.full((B, N), p.v_0, dtype=dt_, device=dev)
        g = torch.zeros((B, N), dtype=dt_, device=dev)
        since = torch.full((B, N), 30000, dtype=torch.int16, device=dev)  # steps since spike (saturating)
        counts = torch.zeros((B, N), dtype=torch.int32, device=dev)
        queue = [None] * d  # ring buffer of (sb, sj) spikes waiting to be delivered

        for t in range(T):
            # 1) state update (groups slot) for non-refractory neurons
            since.add_(1).clamp_(max=30000)
            not_ref = since >= rfc
            v_new = (v - p.v_0).mul_(a_v).add_(g, alpha=k_vg).add_(p.v_0)
            v = torch.where(not_ref, v_new, v)
            g = torch.where(not_ref, g * a_g, g)
            # 2) threshold
            spk = (v > p.v_th) & not_ref
            sb, sj = torch.nonzero(spk, as_tuple=True)
            has = sj.numel() > 0
            if has:
                since[sb, sj] = 0
                not_ref[sb, sj] = False
                counts[sb, sj] += 1
            # 3) synapses: deliver spikes emitted d steps ago; Poisson kicks
            old = queue[t % d]
            if old is not None:
                self._deliver(old[0], old[1], g, not_ref.view(-1))
            queue[t % d] = (sb, sj) if has else None
            if U:
                hit = (rand() < prob) & not_ref[:, uidx]
                v[:, uidx] += kick * hit.to(dt_)
            # 4) reset
            if has:
                v[sb, sj] = p.v_rst
                g[sb, sj] = 0.0
        out = counts.view(E, R, N)
        return out if return_device else out.cpu()


def load_shiu(version="783", root=None):
    """Load Shiu's own model input files (completeness + connectivity) as arrays."""
    import pandas as pd
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from paths import SHIU
    root = Path(root or SHIU)
    files = {"630": ("2023_03_23_completeness_630_final.csv", "2023_03_23_connectivity_630_final.parquet"),
             "783": ("Completeness_783.csv", "Connectivity_783.parquet")}[version]
    comp = pd.read_csv(root / files[0], index_col=0)
    con = pd.read_parquet(root / files[1], columns=["Presynaptic_Index", "Postsynaptic_Index",
                                                    "Excitatory x Connectivity"])
    return (comp.index.values, con["Presynaptic_Index"].values, con["Postsynaptic_Index"].values,
            con["Excitatory x Connectivity"].values)
