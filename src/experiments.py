"""T3.2 / T4.x: run experiment batteries on connectome variants, with a resumable ledger.

Each (variant, battery) is one output file results/runs/<variant_key>/<battery>.npz holding,
for every experiment:
  rate_idx_<k>, rate_val_<k>  sparse per-neuron mean rate (Hz) over trials (only rate > 0)
  ro_<k>                      per-trial rates (n_trials, 4) of MN9_L, MN9_R, aBN1_L, aBN1_R
                              (mean over the neurons of that type and side)
  n_active_<k>                mean number of active neurons per trial
plus 'exps' (names) and 'meta' (JSON). The ledger results/ledger.csv records every finished file.

Batteries
  core   for side in L, R: sugar, bitter, water, JO_CE, JO_F at 150 Hz (Shiu's default rate)
         + sugar 150 & bitter 150                                    -> 12 experiments
  rates  side L: sugar / water / JO_CE / JO_F at 50, 100, 200 Hz; sugar 150 + bitter 50/100/200
  screen every sensory type shared by the three datasets, each side, at 150 Hz

Usage:
  python src/experiments.py --variants main --battery core --device mps
  python src/experiments.py --grid config/grid_cloud.yaml --device cuda   (see scripts/run_sweeps.sh)
"""
from __future__ import annotations

import argparse, json, os, sys, time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import connectome as C  # noqa: E402
import stimuli as S  # noqa: E402
from lif_torch import Network, LIFParams  # noqa: E402

from paths import RESULTS  # noqa: E402
RUNS = RESULTS / "runs"
LEDGER = RUNS.parent / "ledger.csv"
SIDES = ("L", "R")


def battery(neurons, name):
    """Return list of (exp_name, [(idx, rate), ...])."""
    ex = []
    if name in ("core", "core_rep"):
        for s in SIDES:
            for p in ("sugar", "bitter", "water", "JO_CE", "JO_F"):
                ex.append((f"{p}_{s}_150", [(S.stim_idx(neurons, p, s), 150.0)]))
            ex.append((f"sugar+bitter_{s}_150", [(S.stim_idx(neurons, "sugar", s), 150.0),
                                                 (S.stim_idx(neurons, "bitter", s), 150.0)]))
    elif name == "core_bal":
        # D10: both sides stimulated with the same number of neurons (the larger side is
        # randomly subsampled, fixed seed) so side imbalance in typing cannot drive L/R gaps
        rng = np.random.default_rng(20261125)
        for p in ("sugar", "bitter", "water", "JO_CE", "JO_F"):
            idx = {s: S.stim_idx(neurons, p, s) for s in SIDES}
            k = min(len(idx["L"]), len(idx["R"]))
            for s in SIDES:
                sub = np.sort(rng.choice(idx[s], k, replace=False)) if k else idx[s][:0]
                ex.append((f"{p}_{s}_150", [(sub, 150.0)]))
    elif name == "rates":
        s = "L"
        for p in ("sugar", "water", "JO_CE", "JO_F"):
            for r in (50, 100, 200):
                ex.append((f"{p}_{s}_{r}", [(S.stim_idx(neurons, p, s), float(r))]))
        for r in (50, 100, 200):
            ex.append((f"sugar+bitter{r}_{s}_150", [(S.stim_idx(neurons, "sugar", s), 150.0),
                                                    (S.stim_idx(neurons, "bitter", s), float(r))]))
    elif name == "screen":
        for t in screen_types():
            for s in SIDES:
                idx = np.flatnonzero((neurons.type.values == t) & (neurons.side.values == s))
                ex.append((f"screen:{t}_{s}_150", [(idx, 150.0)]))
    else:
        raise ValueError(name)
    return ex


def screen_types():
    """Sensory cell types (FlyWire super_class 'sensory') present on both sides in all three
    datasets' brain subgraphs."""
    fw, _ = C.load("flywire")
    sens = set(fw.loc[fw.superclass == "sensory", "type"].dropna())
    ok = sorted(t for t in sens if t in C.types_shared())
    out = []
    for t in ok:
        good = True
        for d in [d for d in C.DATASETS if (C.STD / d / "neurons.parquet").exists()]:
            n, _ = C.load(d)
            sides = set(n.loc[(n.type == t) & (n.region == "brain"), "side"])
            good &= {"L", "R"} <= sides
        if good:
            out.append(t)
    return out


def auto_rows(n_neurons, device):
    """Rows (trials) per batch: fill ~60% of free GPU memory at ~48 bytes per neuron-row."""
    import torch
    if str(device).startswith("cuda"):
        free, _ = torch.cuda.mem_get_info()
        return int(max(30, min(6000, 0.6 * free / (48 * n_neurons))))
    return 300  # cpu / mps


def ledger_done():
    if not LEDGER.exists():
        return set()
    d = pd.read_csv(LEDGER)
    return set(zip(d.key, d.battery))


def run_variant(variant, bat, device="cpu", n_trials=30, seed=0, max_rows=600, t_run=1000.0):
    key = C.variant_key(variant)
    out = RUNS / key / f"{bat}.npz"
    if out.exists():
        return out
    t0 = time.time()
    neurons, pre, post, w = C.build(variant)
    net = Network(len(neurons), pre, post, w, LIFParams(t_run=t_run), device=device)
    exps = battery(neurons, bat)
    exps = [(k, st) for k, st in exps if all(len(i) for i, _ in st)]  # skip missing stimuli
    ro_idx = [S.readout_idx(neurons, r, s) for r in ("MN9", "aBN1") for s in SIDES]
    if not max_rows:
        max_rows = auto_rows(len(neurons), device)
    per = max(1, max_rows // n_trials)
    res = {}
    seed_base = seed + (1 if bat == "core_rep" else 0) * 7919
    for c0 in range(0, len(exps), per):
        chunk = exps[c0:c0 + per]
        cnt = net.run_batch([st for _, st in chunk], n_trials, seed=seed_base + c0,
                            t_run=t_run).numpy()
        rate = cnt / (t_run / 1000.0)
        print(f"  {key} {bat}: {min(c0 + per, len(exps))}/{len(exps)} exps, "
              f"{time.time() - t0:.0f}s", flush=True)
        for j, (k, _) in enumerate(chunk):
            m = rate[j].mean(0)
            nz = np.flatnonzero(m > 0)
            res[f"rate_idx_{k}"] = nz.astype(np.int32)
            res[f"rate_val_{k}"] = m[nz].astype(np.float32)
            res[f"ro_{k}"] = np.stack([rate[j][:, ix].mean(1) if len(ix) else np.full(n_trials, np.nan)
                                       for ix in ro_idx], 1).astype(np.float32)
            res[f"n_active_{k}"] = np.float32((cnt[j] > 0).sum(1).mean())
    meta = dict(variant=variant, key=key, battery=bat, n_trials=n_trials, t_run=t_run,
                device=str(device), seconds=time.time() - t0, n_neurons=len(neurons),
                n_edges=int(len(pre)), exps=[k for k, _ in exps])
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp.npz")
    np.savez_compressed(tmp, exps=np.array([k for k, _ in exps]), meta=json.dumps(meta), **res)
    tmp.rename(out)
    row = pd.DataFrame([dict(key=key, battery=bat, seconds=meta["seconds"], device=str(device),
                             n_exps=len(exps), finished=time.strftime("%Y-%m-%d %H:%M:%S"))])
    row.to_csv(LEDGER, mode="a", header=not LEDGER.exists(), index=False)
    print(f"[done] {key} {bat}: {len(exps)} exps, {meta['seconds']:.0f}s", flush=True)
    return out


def load_run(path):
    z = np.load(path, allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    out = {}
    for k in z["exps"]:
        out[str(k)] = dict(idx=z[f"rate_idx_{k}"], val=z[f"rate_val_{k}"], ro=z[f"ro_{k}"],
                           n_active=float(z[f"n_active_{k}"]))
    return meta, out


MAIN = [dict(dataset=d, subgraph="brain", threshold=1, norm=nm, sign="own")
        for nm in ("N1", "N0", "N2") for d in C.DATASETS] + \
       [dict(dataset=d, subgraph="brain", threshold=1, norm="N1", sign="nt") for d in C.DATASETS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", default="main", help="main | degrade | shuffle | json list")
    ap.add_argument("--battery", default="core")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--trials", type=int, default=30)
    ap.add_argument("--max_rows", type=int, default=600)
    ap.add_argument("--n", type=int, default=20, help="copies for degrade/shuffle")
    ap.add_argument("--t_run", type=float, default=1000.0)
    a = ap.parse_args()
    if a.variants == "main":
        vs = MAIN
    elif a.variants == "degrade":
        vs = [dict(dataset="flywire", norm=nm, perturb=dict(kind="degrade", seed=s, ref=r))
              for r in ("banc", "malecns") for nm in ("N0", "N1") for s in range(a.n)]
    elif a.variants == "shuffle":
        vs = [dict(dataset=d, norm="N1", perturb=dict(kind="shuffle", seed=s))
              for d in C.DATASETS for s in range(a.n)]
    else:
        vs = json.loads(a.variants)
    for v in vs:
        run_variant(v, a.battery, a.device, a.trials, max_rows=a.max_rows, t_run=a.t_run)


if __name__ == "__main__":
    main()
