"""Load standardised connectomes and build model variants.

A variant is fully described by a dict, e.g.
  {"dataset": "banc", "subgraph": "brain", "threshold": 1, "norm": "N1", "sign": "own",
   "perturb": None | {"kind": "shuffle", "seed": 3} | {"kind": "degrade", "seed": 3, "ref": "banc"}
                | {"kind": "edgenoise", "seed": 3}}

Normalisations (weights are in "synapse units" and are multiplied by W_syn = 0.275 mV in the
simulator):
  N0  raw synapse counts (Shiu's rule, unchanged).
  N1  global density scaling: counts x s_d, with s_d = median input synapses per neuron in
      FlyWire / the same median in dataset d. The median is taken over neurons of the
      "anchor" cell types shared by all three datasets (see types_shared()), excluding the
      readout types. One number per dataset, never tuned on any outcome.
  N2  input fraction: counts / (total input synapses of the postsynaptic neuron) x C, where
      C is the FlyWire anchor median, so a typical FlyWire neuron keeps its weight scale.
Signs:
  own  dataset's own neuron-level sign (FlyWire: Shiu's table)
  nt   harmonised rule applied to the neuron-level nt prediction (FlyWire: top_nt)
  type majority sign of the neuron's cell type within the dataset
"""
from __future__ import annotations

import functools
from pathlib import Path

import numpy as np
import pandas as pd

from paths import ROOT, STD  # noqa: F401
DATASETS = ("flywire", "banc", "malecns")
READOUT_TYPES = ("CB0701", "SAD093")  # MN9, aBN1


@functools.lru_cache(maxsize=4)
def load(name):
    n = pd.read_parquet(STD / name / "neurons.parquet")
    e = pd.read_parquet(STD / name / "edges.parquet")
    return n, e


@functools.lru_cache(maxsize=1)
def types_shared():
    """Cell types present (brain subgraph) in all three datasets."""
    sets = []
    for d in [d for d in DATASETS if (STD / d / "neurons.parquet").exists()]:
        n, _ = load(d)
        sets.append(set(n.loc[n.region == "brain", "type"].dropna().unique()))
    return frozenset.intersection(*map(frozenset, sets))


def _subgraph(n, e, subgraph):
    if subgraph == "cns":
        return n.copy(), e.copy()
    keep = n.region.values == "brain"
    new = -np.ones(len(n), dtype=np.int64)
    new[keep] = np.arange(keep.sum())
    m = keep[e.pre.values] & keep[e.post.values]
    e2 = pd.DataFrame({"pre": new[e.pre.values[m]], "post": new[e.post.values[m]],
                       "n_syn": e.n_syn.values[m]})
    n2 = n.loc[keep].reset_index(drop=True)
    n2["idx"] = np.arange(len(n2))
    return n2, e2


def anchor_median(n, e):
    """Median total input synapses over neurons of shared types (readouts excluded)."""
    insyn = np.bincount(e.post.values, weights=e.n_syn.values, minlength=len(n))
    shared = types_shared() - set(READOUT_TYPES)
    m = n.type.isin(shared).values & (insyn > 0)
    return float(np.median(insyn[m]))


def type_sign(n, sign_col="sign"):
    maj = n.groupby("type")[sign_col].agg(lambda s: 1 if (s > 0).mean() >= 0.5 else -1)
    out = n.type.map(maj)
    return out.fillna(n[sign_col]).astype(np.int8).values


def build(variant, rng_seed_offset=0):
    """Return (neurons_df, pre, post, weight) for a variant. weight is signed, synapse units."""
    v = dict(variant)
    n, e = load(v["dataset"])
    n, e = _subgraph(n, e, v.get("subgraph", "brain"))
    pert = v.get("perturb") or {}
    rng = np.random.default_rng(int(pert.get("seed", 0)) + 1000003 * rng_seed_offset)
    pre, post, cnt = e.pre.values, e.post.values, e.n_syn.values.astype(np.float64)

    if pert.get("kind") == "edgenoise":  # Poisson resampling of synapse counts
        cnt = rng.poisson(cnt).astype(np.float64)
    if pert.get("kind") == "degrade":     # binomial thinning to a reference's per-type deficit
        p_type = degrade_probs(v["dataset"], pert.get("ref", "banc"), v.get("subgraph", "brain"),
                               v.get("threshold", 1))
        p = n.type.map(p_type).fillna(p_type.get("__global__", 1.0)).values[post]
        cnt = rng.binomial(cnt.astype(np.int64), np.clip(p, 0, 1)).astype(np.float64)

    t = v.get("threshold", 1)
    m = cnt >= max(t, 1)
    pre, post, cnt = pre[m], post[m], cnt[m]

    if pert.get("kind") == "shuffle":  # degree-preserving: permute postsynaptic partners
        post = rng.permutation(post)
        keep = pre != post
        df = pd.DataFrame({"pre": pre[keep], "post": post[keep], "c": cnt[keep]})
        df = df.groupby(["pre", "post"], as_index=False).c.sum()
        pre, post, cnt = df.pre.values, df.post.values, df.c.values

    norm = v.get("norm", "N0")
    if norm == "N1":
        fw_n, fw_e = _subgraph(*load("flywire"), v.get("subgraph", "brain"))
        fw_e = fw_e[fw_e.n_syn >= max(t, 1)]
        e_now = pd.DataFrame({"post": post, "n_syn": cnt})
        cnt = cnt * anchor_median(fw_n, fw_e) / anchor_median(n, e_now)
    elif norm == "N2":
        fw_n, fw_e = _subgraph(*load("flywire"), v.get("subgraph", "brain"))
        fw_e = fw_e[fw_e.n_syn >= max(t, 1)]
        insyn = np.bincount(post, weights=cnt, minlength=len(n))
        cnt = cnt / insyn[post] * anchor_median(fw_n, fw_e)

    sign_kind = v.get("sign", "own")
    sgn = {"own": n.sign.values, "nt": n.sign_nt.values,
           "type": type_sign(n)}[sign_kind].astype(np.float64)
    w = cnt * sgn[pre]
    return n, pre.astype(np.int64), post.astype(np.int64), w


@functools.lru_cache(maxsize=8)
def degrade_probs(target, ref, subgraph="brain", threshold=1):
    """Per-postsynaptic-type thinning probability p = min(1, ref median input / target median
    input) over neurons of each shared type. '__global__' holds the median ratio for types
    absent from ref."""
    def per_type(d):
        n, e = _subgraph(*load(d), subgraph)
        e = e[e.n_syn >= max(threshold, 1)]
        insyn = np.bincount(e.post.values, weights=e.n_syn.values, minlength=len(n))
        return pd.Series(insyn, index=n.type.values).groupby(level=0).median()
    a, b = per_type(target), per_type(ref)
    common = a.index.intersection(b.index)
    common = common[(a[common] > 0)]
    ratio = (b[common] / a[common]).clip(upper=1.0)
    out = ratio.to_dict()
    out["__global__"] = float(np.median(ratio.values)) if len(ratio) else 1.0
    return out


def variant_key(v):
    p = v.get("perturb") or {}
    pk = "none" if not p else f"{p['kind']}{p.get('seed', 0)}" + (f"-{p['ref']}" if "ref" in p else "")
    return (f"{v['dataset']}_{v.get('subgraph', 'brain')}_t{v.get('threshold', 1)}_"
            f"{v.get('norm', 'N0')}_{v.get('sign', 'own')}_{pk}")
