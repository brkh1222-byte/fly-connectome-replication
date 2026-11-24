"""Paper figures -> paper/figures/*.pdf and *.png. Each function reads only files in results/.

  fig_validation   PyTorch float32 vs Brian2 per-neuron rates (3 experiments) + readout CIs
  fig_repro        Brian2 reproduction: sugar->MN9 rate curve, v630 vs v783
  fig_datasets     per-type input synapses, BANC / male CNS vs FlyWire
  fig_replication  readout rates per prediction x dataset x normalisation
  fig_ladder       agreement ladder (Spearman rho) with degraded and shuffle distributions
  fig_sweep        robustness: verdicts / rho across the T4.1 grid
  fig_screen       stimulation screen: per-type between-connectome rho vs shuffle floor
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ROOT, RESULTS  # noqa: E402

FIG = ROOT / "paper" / "figures"
COL = {"flywire": "#2b6a99", "banc": "#d0743c", "malecns": "#5a9e5a"}
LAB = {"flywire": "FlyWire v783", "banc": "BANC v888", "malecns": "Male CNS v1.0"}
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                     "pdf.fonttype": 42})


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(FIG / f"{name}.png", dpi=200)
    plt.close(fig)


def fig_validation():
    sys.path.insert(0, str(ROOT / "src"))
    from validate import EXPS, counts_from_parquet
    from lif_torch import load_shiu
    ids = load_shiu("783")[0]
    n = len(ids)
    V = RESULTS / "validation"
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.5))
    for ax, name in zip(axs, EXPS):
        b = counts_from_parquet(V / f"brian2_{name}_s11.parquet", n, 30).mean(0)
        f = V / f"torch-mps_{name}_s21.npy"
        if not f.exists():
            f = V / f"torch-cpu_{name}_s21.npy"
        t = np.load(f).mean(0)
        act = (b > 0) | (t > 0)
        ax.loglog(b[act] + 0.1, t[act] + 0.1, ".", ms=2, alpha=0.5, color="#2b6a99")
        lim = [0.08, 400]
        ax.plot(lim, lim, "k-", lw=0.5)
        r = np.corrcoef(b[act], t[act])[0, 1]
        ax.set_title(f"{name}\nr = {r:.4f} (n = {act.sum()})", fontsize=7)
        ax.set_xlabel("Brian2 (float64) rate + 0.1 (Hz)")
        ax.set_xlim(lim); ax.set_ylim(lim)
    axs[0].set_ylabel("PyTorch float32 rate + 0.1 (Hz)")
    fig.tight_layout()
    save(fig, "fig2_validation")


if __name__ == "__main__":
    for name in sys.argv[1:] or ["fig_validation"]:
        globals()[name]()
