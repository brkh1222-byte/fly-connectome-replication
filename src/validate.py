"""T2.2: validate the PyTorch LIF (src/lif_torch.py) against Brian2 (src/shiu_brian2.py).

Pre-specified criteria (written before the comparison was run; see notes/decisions.md D3):
  For each of the experiments below, on FlyWire v783 with Shiu's full settings (30 trials x 1 s):
  (a) Pearson r of per-neuron mean rates (neurons active in either simulator) between Torch
      and Brian2 is >= r between two independent Brian2 runs (seed ceiling) minus 0.01;
  (b) the readout neuron's 95% CIs (mean +/- 1.96 SEM over trials) overlap;
  (c) total network spike counts per trial do not differ (two-sided Mann-Whitney p > 0.01).
Results go to results/validation/ and results/gpu_validation.md.

Usage: python src/validate.py --device cpu [--device2 mps]
"""
import argparse, json, subprocess, sys, time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from experiments_def import SHIU_SETS, READOUT  # noqa: E402
from lif_torch import Network, load_shiu  # noqa: E402

OUT = ROOT / "results" / "validation"
EXPS = {  # name: (exc set, rate, exc2 set, rate2, readout)
    "sugarR_100Hz": ("sugarR", 100, None, 0, "MN9_L"),
    "sugarR_100Hz_bitterR_100Hz": ("sugarR", 100, "bitterR", 100, "MN9_L"),
    "JO_CE_100Hz": ("JO_CE", 100, None, 0, "aBN1"),
}
N_TRIALS = 30


def counts_from_parquet(path, n, trials):
    df = pd.read_parquet(path)
    c = np.zeros((trials, n), dtype=np.int32)
    c[df.trial.values, df.idx.values] = df.n.values
    return c


def run_brian2(name, spec, seed):
    exc, rate, exc2, rate2, _ = spec
    out = OUT / f"brian2_{name}_s{seed}"
    if not Path(str(out) + ".parquet").exists():
        cmd = ["nice", sys.executable, str(ROOT / "src" / "shiu_brian2.py"), "--version", "783",
               "--exp", exc, "--rate", str(rate), "--trials", str(N_TRIALS), "--seed", str(seed),
               "--out", str(out)]
        if exc2:
            cmd += ["--exp2", exc2, "--rate2", str(rate2)]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    return str(out) + ".parquet"


def run_torch(net, id2i, name, spec, seed, device):
    exc, rate, exc2, rate2, _ = spec
    out = OUT / f"torch-{device}_{name}_s{seed}.npy"
    if out.exists():
        return np.load(out), json.load(open(str(out) + ".json"))["seconds"]
    stim = [([id2i[i] for i in SHIU_SETS[exc] if i in id2i], rate)]
    if exc2:
        stim.append(([id2i[i] for i in SHIU_SETS[exc2] if i in id2i], rate2))
    t0 = time.time()
    c = net.run(N_TRIALS, stim, seed=seed).numpy()
    sec = time.time() - t0
    np.save(out, c)
    json.dump({"seconds": sec}, open(str(out) + ".json", "w"))
    return c, sec


def compare(a, b):
    ra, rb = a.mean(0), b.mean(0)
    act = (ra > 0) | (rb > 0)
    return float(np.corrcoef(ra[act], rb[act])[0, 1]), int(act.sum())


def ci(x):
    m, s = x.mean(), x.std(ddof=1) / np.sqrt(len(x))
    return m, m - 1.96 * s, m + 1.96 * s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--devices", default="cpu", help="comma list, e.g. cpu,mps")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    ids, pre, post, w = load_shiu("783")
    id2i = {j: i for i, j in enumerate(ids)}
    n = len(ids)
    rows = []
    for dev in a.devices.split(","):
        net = Network(n, pre, post, w, device=dev)
        for name, spec in EXPS.items():
            ro = id2i[READOUT[spec[4]]]
            b1 = counts_from_parquet(run_brian2(name, spec, 11), n, N_TRIALS)
            b2 = counts_from_parquet(run_brian2(name, spec, 12), n, N_TRIALS)
            t1, sec = run_torch(net, id2i, name, spec, 21, dev)
            t2, _ = run_torch(net, id2i, name, spec, 22, dev)
            r_bb, n_bb = compare(b1, b2)
            r_tb, n_tb = compare(t1, b1)
            r_tb2, _ = compare(t2, b2)
            r_tt, _ = compare(t1, t2)
            mb, lb, ub = ci(b1[:, ro].astype(float))
            mt, lt, ut = ci(t1[:, ro].astype(float))
            p_tot = stats.mannwhitneyu(b1.sum(1), t1.sum(1)).pvalue
            ok = (min(r_tb, r_tb2) >= r_bb - 0.01) and (lt <= ub and lb <= ut) and p_tot > 0.01
            rows.append(dict(device=dev, experiment=name, readout=spec[4],
                             r_brian2_brian2=r_bb, r_torch_brian2=r_tb, r_torch_brian2_rep=r_tb2,
                             r_torch_torch=r_tt, n_active=n_tb,
                             readout_brian2=mb, readout_brian2_lo=lb, readout_brian2_hi=ub,
                             readout_torch=mt, readout_torch_lo=lt, readout_torch_hi=ut,
                             total_spikes_brian2=b1.sum(1).mean(), total_spikes_torch=t1.sum(1).mean(),
                             p_total_spikes=p_tot, torch_seconds_30trials=sec, PASS=bool(ok)))
            print(rows[-1], flush=True)
    df = pd.DataFrame(rows)
    tag = "_".join(a.devices.split(","))
    df.to_csv(ROOT / "results" / f"gpu_validation_{tag}.csv", index=False)
    with open(ROOT / "results" / f"gpu_validation_{tag}.md", "w") as f:
        f.write("# PyTorch LIF vs Brian2 validation (T2.2)\n\n")
        f.write("FlyWire v783, Shiu parameters, 30 trials x 1 s per run. Brian2 2.9.0 (cython) "
                "seeds 11/12; Torch seeds 21/22. Criteria are in src/validate.py.\n\n")
        f.write(df.round(4).to_markdown(index=False))
        f.write(f"\n\nOverall: {'PASS' if df.PASS.all() else 'FAIL'}\n")
    print("overall", df.PASS.all())


if __name__ == "__main__":
    main()
