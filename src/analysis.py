"""Analysis of experiment batteries: replication table (T3.2), agreement ladder (T3.3),
degraded-FlyWire completeness control and shuffle nulls (T4.2), sweep verdicts (T4.1) and
stimulation screen (T4.3).

Pre-specified criteria (notes/decisions.md D7):
  activation prediction (sugar->MN9, water->MN9, JO-CE->aBN1) replicates in dataset d if
      mean readout rate >= 5 Hz AND >= 20% of FlyWire's rate under the same normalisation
      AND one-sided Wilcoxon signed-rank vs 0 p < 0.05 (Holm-corrected across tests)
  bitter suppression replicates if MN9(sugar+bitter) < MN9(sugar) (one-sided Mann-Whitney,
      Holm) AND relative suppression >= 50%
  JO specificity replicates if aBN1(JO-CE) > aBN1(JO-F) (one-sided Mann-Whitney, Holm)
Readout rate = mean over both sides' neurons of the readout type (MN9: CB0701; aBN1: SAD093).
"""
from __future__ import annotations

import argparse, glob, json, sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import connectome as C  # noqa: E402
import agreement as A  # noqa: E402
import experiments as X  # noqa: E402
from paths import RESULTS  # noqa: E402

PROTOCOLS = ("sugar", "bitter", "water", "JO_CE", "JO_F")
RUN_DIRS = [RESULTS / "runs", RESULTS / "cloud" / "runs"]


def neurons_for(v):
    return C._subgraph(*C.load(v["dataset"]), v.get("subgraph", "brain"))[0]


def get(v, bat="core"):
    key = C.variant_key(v)
    for d in RUN_DIRS:
        p = d / key / f"{bat}.npz"
        if p.exists():
            return X.load_run(p)[1]
    return None


def readout(res, exp, which):
    ro = res[exp]["ro"]  # trials x [MN9_L, MN9_R, aBN1_L, aBN1_R]
    cols = [0, 1] if which == "MN9" else [2, 3]
    return np.nanmean(ro[:, cols], axis=1)


# ---------------------------------------------------------------------- T3.2 replication
def replication(norm="N1", sign="own", threshold=1, subgraph="brain"):
    rows = []
    base = dict(subgraph=subgraph, threshold=threshold, norm=norm, sign=sign)
    fw = get(dict(base, dataset="flywire"))
    if fw is None:
        return pd.DataFrame()
    for d in C.DATASETS:
        res = get(dict(base, dataset=d))
        if res is None:
            continue
        for s in ("L", "R"):
            def m(exp, ro, r=res):
                return readout(r, exp, ro) if exp in r else np.full(30, np.nan)
            tests = []
            for name, exp, ro in (("sugar->MN9", f"sugar_{s}_150", "MN9"),
                                  ("water->MN9", f"water_{s}_150", "MN9"),
                                  ("JO-CE->aBN1", f"JO_CE_{s}_150", "aBN1")):
                x, xf = m(exp, ro), m(exp, ro, fw)
                p = stats.wilcoxon(x, alternative="greater").pvalue if np.nansum(x) > 0 else 1.0
                tests.append(dict(prediction=name, value=np.nanmean(x), flywire=np.nanmean(xf),
                                  p=p, crit=(np.nanmean(x) >= 5) and
                                  (np.nanmean(x) >= 0.2 * np.nanmean(xf))))
            a, b = m(f"sugar+bitter_{s}_150", "MN9"), m(f"sugar_{s}_150", "MN9")
            sup = 1 - np.nanmean(a) / np.nanmean(b) if np.nanmean(b) > 0 else np.nan
            p = stats.mannwhitneyu(a, b, alternative="less").pvalue if np.nanmean(b) > 0 else 1.0
            base_ok = bool(np.nanmean(b) >= 5)  # D13: suppression needs a sugar response to suppress
            if not base_ok:
                sup = np.nan
            tests.append(dict(prediction="bitter suppresses MN9", value=sup,
                              flywire=1 - np.nanmean(m(f"sugar+bitter_{s}_150", "MN9", fw)) /
                              max(np.nanmean(m(f"sugar_{s}_150", "MN9", fw)), 1e-9),
                              p=p, crit=bool(sup >= 0.5) if np.isfinite(sup) else False))
            ce, f = m(f"JO_CE_{s}_150", "aBN1"), m(f"JO_F_{s}_150", "aBN1")
            p = stats.mannwhitneyu(ce, f, alternative="greater").pvalue if np.nansum(ce) > 0 else 1.0
            tests.append(dict(prediction="JO-CE > JO-F at aBN1", value=np.nanmean(ce) - np.nanmean(f),
                              flywire=np.nanmean(m(f"JO_CE_{s}_150", "aBN1", fw)) -
                              np.nanmean(m(f"JO_F_{s}_150", "aBN1", fw)), p=p, crit=bool(np.nanmean(ce) >= 5)))  # D13: needs a JO-CE response
            for t in tests:
                rows.append(dict(dataset=d, side=s, norm=norm, sign=sign, threshold=threshold,
                                 subgraph=subgraph, **t))
    df = pd.DataFrame(rows)
    if len(df):
        mask = df.dataset != "flywire"
        df["p_holm"] = np.nan
        if mask.any():
            df.loc[mask, "p_holm"] = multipletests(df.loc[mask, "p"].fillna(1), method="holm")[1]
        df.loc[~mask, "p_holm"] = df.loc[~mask, "p"]
        df["replicates"] = df.crit & (df.p_holm < 0.05)
    return df


# ---------------------------------------------------------------------- T3.3 ladder
def _prof(v, res, exp):
    names, side = A.protocol_names(exp)
    return A.profile(neurons_for(v), res[exp], side, names)


def ladder(norm="N1", sign="own", threshold=1, subgraph="brain", n_copies=50, n_boot=1000):
    base = dict(subgraph=subgraph, threshold=threshold, norm=norm, sign=sign)
    rows = []

    def add(rung, pair, va, ra, ea, vb, rb, eb, proto, side):
        if ra is None or rb is None or ea not in ra or eb not in rb:
            return
        c = A.compare(_prof(va, ra, ea), _prof(vb, rb, eb), n_boot=n_boot)
        fa = ra[ea]["n_active"] / NN[va["dataset"]]
        fb = rb[eb]["n_active"] / NN[vb["dataset"]]
        rows.append(dict(rung=rung, pair=pair, protocol=proto, side=side, norm=norm, sign=sign,
                         threshold=threshold, frac_active_a=fa, frac_active_b=fb,
                         any_runaway=bool(max(fa, fb) > 0.02), **c))

    V = {d: dict(base, dataset=d) for d in C.DATASETS}
    NN = {d: len(neurons_for(V[d])) for d in C.DATASETS}
    R = {d: get(V[d]) for d in C.DATASETS}
    Rr = {d: get(V[d], "core_rep") for d in C.DATASETS}
    Rb = {d: get(V[d], "core_bal") for d in C.DATASETS}
    for p in PROTOCOLS:
        for d in C.DATASETS:  # D10: hemisphere rung with side-balanced stimulus counts
            add("hemisphere_balanced", f"{d}L|{d}R", V[d], Rb[d], f"{p}_L_150", V[d], Rb[d],
                f"{p}_R_150", p, "L/R")
    for p in PROTOCOLS:
        for s in ("L", "R"):
            e = f"{p}_{s}_150"
            for d in C.DATASETS:
                add("seed", f"{d}|{d}", V[d], R[d], e, V[d], Rr[d], e, p, s)
            for d in C.DATASETS:
                if s == "L":
                    add("hemisphere", f"{d}L|{d}R", V[d], R[d], f"{p}_L_150", V[d], R[d],
                        f"{p}_R_150", p, "L/R")
            for a, b in (("flywire", "banc"), ("flywire", "malecns"), ("banc", "malecns")):
                add("between", f"{a}|{b}", V[a], R[a], e, V[b], R[b], e, p, s)
            for ref in ("banc", "malecns"):
                for k in range(n_copies):
                    vd = dict(dataset="flywire", subgraph=subgraph, threshold=threshold, norm=norm,
                              sign=sign, perturb=dict(kind="degrade", seed=k, ref=ref))
                    rd = get(vd)
                    if rd is None:
                        continue
                    add(f"degraded->{ref}", f"flywire|flywire-deg-{ref}#{k}", V["flywire"],
                        R["flywire"], e, vd, rd, e, p, s)
            for d in C.DATASETS:
                for k in range(n_copies):
                    vs = dict(dataset=d, subgraph=subgraph, threshold=threshold, norm=norm,
                              sign=sign, perturb=dict(kind="shuffle", seed=k))
                    rs = get(vs)
                    if rs is None:
                        continue
                    add("shuffle", f"{d}|{d}-shuf#{k}", V[d], R[d], e, vs, rs, e, p, s)
    return pd.DataFrame(rows)


def activity(norms, signs=("own", "nt")):
    """Mean number of active neurons and readout rates for every base run that exists."""
    rows = []
    for nm in norms:
        for sg in signs:
            for d in C.DATASETS:
                v = dict(dataset=d, subgraph="brain", threshold=1, norm=nm, sign=sg)
                res = get(v)
                if res is None:
                    continue
                n = len(neurons_for(v))
                for exp, r in res.items():
                    rows.append(dict(dataset=d, norm=nm, sign=sg, exp=exp, n_active=r["n_active"],
                                     frac_active=r["n_active"] / n,
                                     runaway=bool(r["n_active"] / n > 0.02),
                                     MN9=float(np.nanmean(r["ro"][:, :2])),
                                     aBN1=float(np.nanmean(r["ro"][:, 2:]))))
    return pd.DataFrame(rows)


def control_readouts(norms=("N0", "N1"), n_copies=50):
    """Readout rates and activity for FlyWire, BANC, degraded-FlyWire copies and shuffles."""
    rows = []
    for nm in norms:
        vs = [("flywire", dict(dataset="flywire", norm=nm)), ("banc", dict(dataset="banc", norm=nm)),
              ("malecns", dict(dataset="malecns", norm=nm))]
        for k in range(n_copies):
            vs.append((f"flywire-degraded-banc", dict(dataset="flywire", norm=nm,
                       perturb=dict(kind="degrade", seed=k, ref="banc"))))
            for d in C.DATASETS:
                vs.append((f"{d}-shuffle", dict(dataset=d, norm=nm, perturb=dict(kind="shuffle", seed=k))))
        for label, v in vs:
            res = get(v)
            if res is None:
                continue
            n = len(neurons_for(v))
            for exp, r in res.items():
                rows.append(dict(network=label, norm=nm, seed=(v.get("perturb") or {}).get("seed", -1),
                                 exp=exp, MN9=float(np.nanmean(r["ro"][:, :2])),
                                 aBN1=float(np.nanmean(r["ro"][:, 2:])), n_active=r["n_active"],
                                 runaway=bool(r["n_active"] / n > 0.02)))
    return pd.DataFrame(rows)


def completeness_test(lad):
    """H3 per protocol and side: is the observed FlyWire-BANC rho inside the range of
    FlyWire vs degraded-FlyWire(->BANC) copies? (2.5-97.5% range; with few copies = min-max.)"""
    rows = []
    for (nm, pr, sd), d in lad[lad.rung.isin(["between", "degraded->banc"])].groupby(["norm", "protocol", "side"]):
        obs = d[(d.rung == "between") & (d.pair == "flywire|banc")].rho
        deg = d[d.rung == "degraded->banc"].rho.dropna()
        if len(obs) and len(deg):
            lo, hi = np.percentile(deg, [2.5, 97.5])
            rows.append(dict(norm=nm, protocol=pr, side=sd, rho_flywire_banc=float(obs.iloc[0]),
                             deg_median=float(deg.median()), deg_lo=float(lo), deg_hi=float(hi),
                             n_copies=len(deg),
                             inside=bool(lo <= obs.iloc[0] <= hi) if np.isfinite(obs.iloc[0]) else None,
                             below=bool(obs.iloc[0] < lo) if np.isfinite(obs.iloc[0]) else None))
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--norms", default="N0,N1,N2")
    ap.add_argument("--n_boot", type=int, default=1000)
    a = ap.parse_args()
    out = RESULTS
    reps, lads = [], []
    for nm in a.norms.split(","):
        reps.append(replication(norm=nm))
        lads.append(ladder(norm=nm, n_boot=a.n_boot))
    rep = pd.concat(reps)
    lad = pd.concat(lads)
    control_readouts().to_csv(out / "control_readouts.csv", index=False)
    act = activity(a.norms.split(","))
    act.to_csv(out / "activity_table.csv", index=False)
    rep.to_csv(out / "replication_table.csv", index=False)
    if len(lad):
        completeness_test(lad).to_csv(out / "completeness_test.csv", index=False)
    lad.to_csv(out / "agreement_ladder.csv", index=False)
    if len(lad):
        lad = lad.assign(pairbase=lad.pair.str.replace(r"#\d+", "", regex=True))
        summ = lad.groupby(["norm", "rung", "pairbase"]).agg(
            rho_median=("rho", "median"), rho_mean=("rho", "mean"),
            rho_q05=("rho", lambda x: x.quantile(0.05)), rho_q95=("rho", lambda x: x.quantile(0.95)),
            jaccard_median=("jaccard", "median"), n=("rho", "count")).reset_index()
        summ.to_csv(out / "agreement_summary.csv", index=False)
        calm = lad[~lad.any_runaway].groupby(["norm", "rung", "pairbase"]).agg(
            rho_median=("rho", "median"), rho_mean=("rho", "mean"),
            jaccard_median=("jaccard", "median"), n=("rho", "count")).reset_index()
        calm.to_csv(out / "agreement_summary_no_runaway.csv", index=False)  # exploratory (D11)
        print("no-runaway pairs only (exploratory):"); print(calm.to_string())
        print(summ.to_string())
    print(rep.to_string())


if __name__ == "__main__":
    main()
