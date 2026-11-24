"""T3.3: cell-type-level agreement between simulated response profiles.

Profile of one experiment: mean firing rate of each (cell type, side relative to the
stimulated side: ipsi / contra / mid) group, averaged over all neurons of the group (silent
neurons count as 0). The stimulated types are excluded. Comparisons use only types present in
both networks.

Metrics (pre-specified; the 2 Hz threshold follows cerebro-mosca so numbers are comparable):
  rho      Spearman correlation of log(1 + rate) over groups active (>= 2 Hz) in either profile
  jaccard  |A & B| / |A | B| of the active group sets
  topk     Jaccard overlap of the k = 20 / 50 most active groups
95% CIs: 1,000 bootstrap resamples over groups.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

import stimuli as S

THR = 2.0


def profile(neurons, entry, stim_side, stim_names):
    rate = np.zeros(len(neurons), dtype=np.float64)
    rate[entry["idx"]] = entry["val"]
    side = neurons.side.values
    rel = np.where(side == stim_side, "ipsi",
                   np.where(np.isin(side, ["L", "R"]), "contra", "mid"))
    t = neurons.type.values
    excl = set()
    for nm in stim_names:
        excl |= set(S.stim_types(neurons, nm))
    df = pd.DataFrame({"type": t, "rel": rel, "r": rate})
    df = df[df.type.notna() & ~df.type.isin(excl)]
    return df.groupby(["type", "rel"]).r.mean()


def compare(pa, pb, thr=THR, n_boot=1000, seed=0, ks=(20, 50)):
    common = pa.index.intersection(pb.index)
    a, b = pa.loc[common].values, pb.loc[common].values
    act = (a >= thr) | (b >= thr)
    out = dict(n_common=int(len(common)), n_active=int(act.sum()))
    if act.sum() < 5:
        return dict(out, rho=np.nan, rho_lo=np.nan, rho_hi=np.nan, jaccard=np.nan,
                    **{f"top{k}": np.nan for k in ks})
    la, lb = np.log1p(a[act]), np.log1p(b[act])
    out["rho"] = float(stats.spearmanr(la, lb).statistic)
    A, B = a >= thr, b >= thr
    out["jaccard"] = float((A & B).sum() / max((A | B).sum(), 1))
    for k in ks:
        ta, tb = set(np.argsort(-a)[:k]), set(np.argsort(-b)[:k])
        out[f"top{k}"] = len(ta & tb) / len(ta | tb)
    rng = np.random.default_rng(seed)
    bs = []
    n = len(la)
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        r = stats.spearmanr(la[i], lb[i]).statistic
        if np.isfinite(r):
            bs.append(r)
    out["rho_lo"], out["rho_hi"] = (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))) \
        if bs else (np.nan, np.nan)
    return out


def protocol_names(exp):
    """'sugar+bitter_L_150' -> (['sugar','bitter'], 'L')."""
    head, side, _ = exp.rsplit("_", 2) if exp.count("_") >= 2 else (exp, "L", "")
    head = head.replace("screen:", "")
    names = [h for h in head.split("+")]
    names = [n.rstrip("0123456789") for n in names]
    return [n for n in names if n in S.STIM], side
