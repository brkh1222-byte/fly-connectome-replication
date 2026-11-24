"""T2.1: reproduce Shiu et al. (2024) headline results with their own Brian2 model.

Runs (Brian2, Shiu's exact neuron lists and parameters, 30 trials x 1 s each):
  * sugar GRNs (right; 21 ids) at 20..200 Hz -> MN9 (Fig. 1), on v630 (as published) and v783
  * sugar 100 Hz + bitter 0/50/100/200 Hz -> MN9 (Fig. 3a slice), v783
  * water GRNs at 100/200/260 Hz -> MN9 (Fig. 4), v783
  * JO-CE vs JO-F at 100/160/220 Hz -> aBN1 (Fig. 5g), v783
Outputs: results/brian2/*.parquet (spike counts), results/repro_shiu.csv, results/repro_sugar_mn9.png
"""
import subprocess, sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from experiments_def import READOUT  # noqa: E402
from paths import SHIU  # noqa: E402

OUT = ROOT / "results" / "brian2"
RUNS = []
for ver in ("630", "783"):
    for f in range(20, 201, 20):
        RUNS.append((ver, "sugarR", f, None, 0, "MN9_L"))
for b in (0, 50, 100, 200):
    RUNS.append(("783", "sugarR", 100, "bitterR", b, "MN9_L"))
for f in (100, 200, 260):
    RUNS.append(("783", "waterR", f, None, 0, "MN9_L"))
for f in (100, 160, 220):
    RUNS.append(("783", "JO_CE", f, None, 0, "aBN1"))
    RUNS.append(("783", "JO_F", f, None, 0, "aBN1"))


def name(r):
    ver, e, f, e2, f2, _ = r
    return f"v{ver}_{e}_{f}Hz" + (f"_{e2}_{f2}Hz" if e2 else "")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in RUNS:
        ver, e, f, e2, f2, ro = r
        out = OUT / name(r)
        if not Path(str(out) + ".parquet").exists():
            cmd = ["nice", sys.executable, str(ROOT / "src" / "shiu_brian2.py"), "--version", ver,
                   "--exp", e, "--rate", str(f), "--trials", "30", "--seed", "5", "--out", str(out)]
            if e2:
                cmd += ["--exp2", e2, "--rate2", str(f2)]
            print(" ".join(cmd[2:]), flush=True)
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        comp = pd.read_csv(SHIU / ("Completeness_783.csv" if ver == "783"
                                   else "2023_03_23_completeness_630_final.csv"), index_col=0)
        i = list(comp.index).index(READOUT[ro])
        d = pd.read_parquet(str(out) + ".parquet")
        per = np.zeros(30)
        s = d[d.idx == i].set_index("trial").n
        per[s.index.values] = s.values
        act = d.groupby("trial").size()
        rows.append(dict(run=name(r), version=ver, stim=e, rate=f, stim2=e2, rate2=f2, readout=ro,
                         mean_hz=per.mean(), sem_hz=per.std(ddof=1) / np.sqrt(30),
                         n_active_mean=act.mean()))
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "results" / "repro_shiu.csv", index=False)
    plot(df)
    print(df.to_string())


def plot(df):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    for ver, c in (("630", "#1f5f8b"), ("783", "#c4572a")):
        s = df[(df.version == ver) & (df.stim == "sugarR") & df.stim2.isna()].sort_values("rate")
        ax.errorbar(s.rate, s.mean_hz, yerr=1.96 * s.sem_hz, marker="o", ms=3, color=c,
                    label=f"FlyWire v{ver}", capsize=2, lw=1.2)
    ax.set_xlabel("Sugar GRN Poisson rate (Hz)")
    ax.set_ylabel("MN9 firing rate (Hz)")
    ax.set_title("Brian2 reproduction of Shiu et al. Fig. 1", fontsize=9)
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(ROOT / "results" / "repro_sugar_mn9.png", dpi=200)


if __name__ == "__main__":
    main()
