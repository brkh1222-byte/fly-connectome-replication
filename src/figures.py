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


def fig_repro():
    df = pd.read_csv(RESULTS / "repro_shiu.csv")
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.4))
    for ver, c in (("630", "#2b6a99"), ("783", "#d0743c")):
        d = df[(df.version.astype(str) == ver) & (df.stim == "sugarR") & df.stim2.isna()].sort_values("rate")
        if ver == "783":
            d = d[d.run.str.fullmatch(r"v783_sugarR_\d+Hz")]
        axs[0].errorbar(d.rate, d.mean_hz, yerr=1.96 * d.sem_hz, marker="o", ms=3, color=c,
                        capsize=2, lw=1, label=f"FlyWire v{ver}")
    axs[0].set_xlabel("Sugar GRN rate (Hz)"); axs[0].set_ylabel("MN9 rate (Hz)")
    axs[0].legend(frameon=False, fontsize=7)
    d = df[df.stim2 == "bitterR"].sort_values("rate2")
    axs[1].errorbar(d.rate2, d.mean_hz, yerr=1.96 * d.sem_hz, marker="o", ms=3, color="#d0743c", capsize=2, lw=1)
    axs[1].set_xlabel("Bitter GRN rate (Hz), sugar at 100 Hz"); axs[1].set_ylabel("MN9 rate (Hz)")
    for st, c in (("JO_CE", "#2b6a99"), ("JO_F", "#999999")):
        d = df[df.stim == st].sort_values("rate")
        axs[2].errorbar(d.rate, d.mean_hz, yerr=1.96 * d.sem_hz, marker="o", ms=3, color=c, capsize=2, lw=1,
                        label=st.replace("_", "-"))
    axs[2].set_xlabel("JO neuron rate (Hz)"); axs[2].set_ylabel("aBN1 rate (Hz)")
    axs[2].legend(frameon=False, fontsize=7)
    fig.tight_layout(); save(fig, "fig1_repro")


def fig_datasets():
    t = pd.read_csv(RESULTS / "type_input_comparison.csv", index_col=0)
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 2.8), sharey=False)
    for ax, d in zip(axs, ("banc", "malecns")):
        m = (t.flywire > 0) & (t[d] > 0)
        ax.loglog(t.flywire[m], t[d][m], ".", ms=1.5, alpha=0.3, color=COL[d])
        lim = [1, 3e4]; ax.plot(lim, lim, "k-", lw=0.5)
        r = np.median(t[d][m] / t.flywire[m])
        ax.plot(lim, [lim[0] * r, lim[1] * r], "--", lw=0.8, color="k")
        ax.set_title(f"{LAB[d]}: median ratio {r:.2f} (n = {m.sum()} types)", fontsize=7)
        ax.set_xlabel("FlyWire: median input synapses per neuron"); ax.set_ylabel(LAB[d])
        ax.set_xlim(lim); ax.set_ylim(lim)
    fig.tight_layout(); save(fig, "fig3_datasets")


def fig_replication():
    df = pd.read_csv(RESULTS / "replication_table.csv")
    preds = ["sugar->MN9", "water->MN9", "JO-CE->aBN1", "bitter suppresses MN9", "JO-CE > JO-F at aBN1"]
    norms = [n for n in ("N0", "N1", "N2") if n in set(df.norm)]
    fig, axs = plt.subplots(len(norms), len(preds), figsize=(7.4, 1.7 * len(norms) + 0.4), squeeze=False)
    for i, nm in enumerate(norms):
        for j, pr in enumerate(preds):
            ax = axs[i, j]
            d = df[(df.norm == nm) & (df.prediction == pr)]
            x = 0
            for ds in ("flywire", "banc", "malecns"):
                for sd in ("L", "R"):
                    r = d[(d.dataset == ds) & (d.side == sd)]
                    if len(r):
                        ok = bool(r.replicates.iloc[0])
                        ax.bar(x, r.value.iloc[0], color=COL[ds], alpha=1.0 if ok else 0.35,
                               hatch=None if sd == "L" else "//", edgecolor="white", lw=0.3)
                    x += 1
                x += 0.5
            if i == 0:
                ax.set_title(pr.replace("->", " → "), fontsize=7)
            if j == 0:
                ax.set_ylabel(f"{nm}\nHz" , fontsize=7)
            ax.set_xticks([])
    fig.text(0.5, 0.005, "bars: FlyWire | BANC | male CNS; plain = left stimulus, hatched = right; "
             "pale = criterion not met; suppression panel is a fraction", ha="center", fontsize=6)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); save(fig, "fig4_replication")


def fig_ladder(norm="N1"):
    lad = pd.read_csv(RESULTS / "agreement_ladder.csv")
    lad = lad[(lad.norm == norm) & (lad.sign == "own")].copy()
    lad["pairbase"] = lad.pair.str.replace(r"#\d+", "", regex=True)
    order = [("seed", None), ("hemisphere", None), ("hemisphere_balanced", None),
             ("degraded->banc", None), ("between", "flywire|banc"), ("between", "flywire|malecns"),
             ("between", "banc|malecns"), ("shuffle", None)]
    names = ["seed", "hemisphere", "hemisphere\n(balanced)", "FlyWire vs\ndegraded→BANC",
             "FlyWire–BANC", "FlyWire–\nmale CNS", "BANC–\nmale CNS", "shuffle"]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    rng = np.random.default_rng(0)
    mk = {"sugar": "o", "bitter": "s", "water": "^", "JO_CE": "D", "JO_F": "v"}
    for x, (rung, pb) in enumerate(order):
        d = lad[lad.rung == rung]
        if pb:
            d = d[d.pairbase == pb]
        d = d.dropna(subset=["rho"])
        for (pr, ra), dd in d.groupby(["protocol", "any_runaway"]):
            ax.plot(x + rng.uniform(-0.25, 0.25, len(dd)), dd.rho, mk.get(pr, "o"), ms=3.5, alpha=0.7,
                    color="#444444", mfc="none" if ra else "#444444", mew=0.6)
        if len(d):
            ax.plot([x - 0.3, x + 0.3], [d.rho.median()] * 2, "-", color="#c0392b", lw=1.5)
    ax.axhline(0, color="k", lw=0.4)
    ax.set_xticks(range(len(names))); ax.set_xticklabels(names, fontsize=6.5)
    ax.set_ylabel("Spearman ρ of cell-type response profiles")
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker=m, ls="", color="#444444", ms=3.5, label=k.replace("_", "-")) for k, m in mk.items()]
    h.append(Line2D([], [], marker="o", ls="", color="#444444", mfc="none", ms=3.5, label="brain-wide activity in either network"))
    ax.legend(handles=h, frameon=False, fontsize=6, ncol=3, loc="upper right")
    ax.set_title(f"Agreement ladder ({norm}, Shiu signs), PRELIMINARY Mac-scale; red = median", fontsize=7)
    fig.tight_layout(); save(fig, f"fig5_ladder_{norm}")


if __name__ == "__main__":
    for name in sys.argv[1:] or ["fig_validation"]:
        globals()[name]()
