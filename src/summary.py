"""T1.4 summary statistics per dataset -> results/dataset_summary.csv and
results/type_input_comparison.csv (per shared cell type: median input synapses per neuron)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import connectome as C  # noqa: E402
import stimuli as S  # noqa: E402
from paths import RESULTS, STD  # noqa: E402


def main():
    rows, per_type = [], {}
    avail = [d for d in C.DATASETS if (STD / d / "neurons.parquet").exists()]
    for d in avail:
        for sub in ("brain", "cns"):
            n, e = C._subgraph(*C.load(d), sub)
            insyn = np.bincount(e.post.values, weights=e.n_syn.values, minlength=len(n))
            outsyn = np.bincount(e.pre.values, weights=e.n_syn.values, minlength=len(n))
            r = dict(dataset=d, subgraph=sub, neurons=len(n), edges=len(e),
                     synapses=int(e.n_syn.sum()),
                     synapses_per_neuron=float(e.n_syn.sum() / len(n)),
                     edges_ge5=int((e.n_syn >= 5).sum()),
                     frac_edges_lt5=float((e.n_syn < 5).mean()),
                     typed_frac=float(n.type.notna().mean()),
                     inhibitory_neuron_frac=float((n.sign < 0).mean()),
                     inhibitory_synapse_frac=float((outsyn[n.sign.values < 0]).sum() / outsyn.sum()),
                     median_input_anchor=C.anchor_median(n, e) if len(avail) > 1 else np.nan)
            for nm in S.STIM:
                for s in ("L", "R"):
                    r[f"n_{nm}_{s}"] = len(S.stim_idx(n, nm, s))
            for ro in S.READOUTS:
                ix = S.readout_idx(n, ro)
                r[f"n_{ro}"] = len(ix)
                r[f"input_{ro}"] = float(insyn[ix].mean()) if len(ix) else np.nan
            rows.append(r)
            if sub == "brain":
                per_type[d] = pd.Series(insyn, index=n.type.values).groupby(level=0).median()
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "dataset_summary.csv", index=False)
    print(df.T.to_string())
    if len(per_type) > 1:
        shared = sorted(C.types_shared())
        t = pd.DataFrame({d: per_type[d].reindex(shared) for d in per_type})
        t.index.name = "type"
        t.to_csv(RESULTS / "type_input_comparison.csv")
        for d in per_type:
            if d != "flywire":
                ratio = (t[d] / t["flywire"]).replace([np.inf, -np.inf], np.nan).dropna()
                print(f"{d}/flywire median per-type input ratio: {ratio.median():.3f} "
                      f"(IQR {ratio.quantile(.25):.3f}-{ratio.quantile(.75):.3f}, n={len(ratio)})")


if __name__ == "__main__":
    main()
