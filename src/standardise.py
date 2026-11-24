"""T1.4: convert FlyWire v783, BANC v888 and male CNS v1.0 to one format.

Output per dataset in data/std/<name>/:
  neurons.parquet: idx (0..N-1), id (int64 root/body id), type (FlyWire-harmonised cell type),
                   side (L/R/M/NA), superclass, region ('brain' | 'vnc' | 'neck' | ...),
                   nt (neuron-level predicted transmitter), sign (+1/-1 used by the model),
                   sign_nt (sign from the harmonised rule applied to nt)
  edges.parquet:   pre, post (idx), n_syn (int32 synapse count, unthresholded as released)

Sign rule (Shiu et al. 2024): GABA and glutamate are inhibitory (-1); acetylcholine and all
other transmitters (dopamine, serotonin, octopamine, histamine, unknown) are excitatory (+1).
FlyWire's model sign is taken from Shiu's own v783 connectivity table (exact replication). BANC
and the male CNS use their own neuron-level predictions with the same rule.

Usage: python src/standardise.py [flywire|banc|malecns|all]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ROOT, RAW, STD, SHIU  # noqa: E402,F401
INHIB = {"gaba", "glutamate"}


def nt_sign(nt):
    nt = pd.Series(nt).astype("string").str.lower()
    return np.where(nt.isin(INHIB), -1, 1).astype(np.int8)


def side_norm(s):
    m = {"left": "L", "right": "R", "center": "M", "l": "L", "r": "R", "m": "M", "c": "M"}
    return pd.Series(s).astype("string").str.lower().map(m).fillna("NA").values


def save(name, neurons, edges):
    out = STD / name
    out.mkdir(parents=True, exist_ok=True)
    neurons = neurons.reset_index(drop=True)
    neurons["idx"] = np.arange(len(neurons), dtype=np.int64)
    neurons.to_parquet(out / "neurons.parquet")
    edges = edges[edges.n_syn > 0].reset_index(drop=True)
    edges["pre"] = edges.pre.astype(np.int32)
    edges["post"] = edges.post.astype(np.int32)
    edges["n_syn"] = edges.n_syn.astype(np.int32)
    edges.to_parquet(out / "edges.parquet")
    print(f"{name}: {len(neurons)} neurons, {len(edges)} edges, {edges.n_syn.sum()} synapses")


# ----------------------------------------------------------------------------------------
def flywire():
    shiu = SHIU
    comp = pd.read_csv(shiu / "Completeness_783.csv", index_col=0)
    con = pd.read_parquet(shiu / "Connectivity_783.parquet",
                          columns=["Presynaptic_Index", "Postsynaptic_Index", "Connectivity",
                                   "Excitatory"])
    ann = pd.read_csv(RAW / "flywire_783" / "Supplemental_file1_neuron_annotations.tsv",
                      sep="\t", low_memory=False,
                      usecols=["root_id", "super_class", "cell_class", "cell_type",
                               "hemibrain_type", "side", "top_nt", "flow"])
    ann = ann.drop_duplicates("root_id").set_index("root_id").reindex(comp.index)
    n = pd.DataFrame({"id": comp.index.values.astype(np.int64)})
    n["type"] = ann.cell_type.values
    n["side"] = side_norm(ann.side.values)
    n["superclass"] = ann.super_class.values
    n["cell_class"] = ann.cell_class.values
    n["region"] = "brain"
    n["nt"] = ann.top_nt.values
    n["sign_nt"] = nt_sign(n.nt)
    shiu_sign = con.groupby("Presynaptic_Index").Excitatory.first()
    n["sign"] = n.sign_nt.values
    n.loc[shiu_sign.index, "sign"] = shiu_sign.values.astype(np.int8)
    e = pd.DataFrame({"pre": con.Presynaptic_Index.values, "post": con.Postsynaptic_Index.values,
                      "n_syn": con.Connectivity.values})
    save("flywire", n, e)


def flywire_types():
    f = STD / "flywire" / "neurons.parquet"
    if not f.exists():
        flywire()
    return set(pd.read_parquet(f, columns=["type"]).type.dropna())


def harmonise(own, fw_match):
    fwt = flywire_types()
    own = pd.Series(own).astype("string").reset_index(drop=True)
    fm = pd.Series(fw_match).astype("string").reset_index(drop=True)
    out = own.where(own.isin(fwt), fm.where(fm.isin(fwt), own))
    return out.astype(object).where(out.notna(), None).values


# ----------------------------------------------------------------------------------------
MCNS_VNC = ("vnc_", "ENS", "efferent_ascending")


def malecns():
    d = RAW / "male_cns_v1.0"
    ann = pd.read_feather(d / "body-annotations-male-cns-v1.0-minconf-0.5.feather",
                          columns=["bodyId", "type", "flywireType", "superclass", "class",
                                   "somaSide", "rootSide", "status"])
    ann = ann[ann.status == "Traced"].drop_duplicates("bodyId")
    nt = pd.read_feather(d / "body-neurotransmitters-male-cns-v1.0.feather",
                         columns=["body", "predicted_nt", "consensus_nt"]).drop_duplicates("body")
    ann = ann.merge(nt, left_on="bodyId", right_on="body", how="left")
    pre_c, post_c, w_c = "body_pre", "body_post", "weight"
    w = pd.read_feather(d / "connectome-weights-male-cns-v1.0-minconf-0.5-traced-only.feather",
                        columns=[pre_c, post_c, w_c])
    keep = set(ann.bodyId.values)
    w = w[w[pre_c].isin(keep) & w[post_c].isin(keep)]
    n = pd.DataFrame({"id": ann.bodyId.values.astype(np.int64)})
    # FlyWire-harmonised type: the male CNS type if it is a FlyWire type name (male CNS types
    # are often finer than its 'flywireType', e.g. LB3a/b/c vs 'LB3'); else 'flywireType' if
    # that is a single FlyWire type; else the male CNS type (counts as unmatched).
    n["type"] = harmonise(ann.type, ann.flywireType)
    n["type_mcns"] = ann.type.values
    side = ann.somaSide.where(ann.somaSide.isin(["L", "R", "M"]), ann.rootSide)
    n["side"] = side_norm(side.values)
    n["superclass"] = ann.superclass.values
    n["cell_class"] = ann["class"].values
    sc = ann.superclass.fillna("").astype(str)
    n["region"] = np.where(sc.str.startswith(MCNS_VNC), "vnc", "brain")
    n["nt"] = ann.predicted_nt.values
    n["sign_nt"] = nt_sign(n.nt)
    n["sign"] = n.sign_nt.values
    id2i = pd.Series(np.arange(len(n)), index=n.id.values)
    e = pd.DataFrame({"pre": id2i.loc[w[pre_c].values].values,
                      "post": id2i.loc[w[post_c].values].values,
                      "n_syn": w[w_c].values})
    e = e.groupby(["pre", "post"], as_index=False).n_syn.sum()
    save("malecns", n, e)


# ----------------------------------------------------------------------------------------
ALIASES = {"MN9": "CB0701"}  # MN9 is FlyWire type CB0701 (male CNS flywireType of MN9)


def banc():
    """BANC v888: proofread neurons only (cf. FlyWire proofread, male CNS Traced); glia and
    non-neurons dropped. Type = reviewed/automatic FlyWire match ('fafb_cell_type', 'auto:'
    prefix stripped) if it is a FlyWire type, else BANC 'cell_type' if it is one, else unmatched.
    Region: central_brain + optic_lobe = brain; ventral_nerve_cord = vnc; missing = unknown.
    Signs from the neuron-level 'neurotransmitter_predicted' (NOT the per-type consensus column,
    which cerebro-mosca found inconsistent for 68 types). Edges: synapse table v2."""
    d = RAW / "banc_888"
    m = pd.read_feather(d / "banc_888_meta.feather",
                        columns=["banc_888_id", "proofread", "side", "region", "super_class",
                                 "cell_class", "cell_type", "fafb_cell_type",
                                 "neurotransmitter_predicted"])
    m = m[(m.proofread.astype(str).str.upper() == "TRUE") &
          ~m.super_class.isin(["glia", "not_a_neuron"])].drop_duplicates("banc_888_id")
    fwt = flywire_types()
    fafb = m.fafb_cell_type.astype("string").str.replace("auto:", "", regex=False)
    own = m.cell_type.astype("string").replace(ALIASES)
    fafb = fafb.replace(ALIASES)
    typ = fafb.where(fafb.isin(fwt), own.where(own.isin(fwt), own))
    n = pd.DataFrame({"id": m.banc_888_id.astype(np.int64).values})
    n["type"] = typ.astype(object).where(typ.notna(), None).values
    n["type_banc"] = m.cell_type.values
    n["side"] = side_norm(m.side.values)
    n["superclass"] = m.super_class.values
    n["cell_class"] = m.cell_class.values
    reg = m.region.astype(str).values
    n["region"] = np.where(np.isin(reg, ["central_brain", "optic_lobe"]), "brain",
                           np.where(reg == "ventral_nerve_cord", "vnc", "unknown"))
    n["nt"] = m.neurotransmitter_predicted.values
    n["sign_nt"] = nt_sign(n.nt)
    n["sign"] = n.sign_nt.values
    import pyarrow.feather as pf
    e = pf.read_table(d / "banc_888_edgelist_simple_v2.feather",
                      columns=["pre", "post", "count"]).to_pandas()
    id2i = pd.Series(np.arange(len(n)), index=n.id.values)
    pre = pd.to_numeric(e["pre"]).values.astype(np.int64)
    post = pd.to_numeric(e["post"]).values.astype(np.int64)
    keep = np.isin(pre, n.id.values) & np.isin(post, n.id.values)
    e2 = pd.DataFrame({"pre": id2i.loc[pre[keep]].values, "post": id2i.loc[post[keep]].values,
                       "n_syn": e["count"].values[keep]})
    e2 = e2.groupby(["pre", "post"], as_index=False).n_syn.sum()
    save("banc", n, e2)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn in (("flywire", flywire), ("malecns", malecns), ("banc", banc)):
        if which in (name, "all"):
            fn()
