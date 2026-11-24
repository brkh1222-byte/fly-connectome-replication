"""T3.1: cross-dataset cell-type matching table and coverage report.

Every standardised dataset carries a FlyWire-harmonised `type` column (see standardise.py):
  FlyWire  Schlegel et al. 2024 cell_type
  male CNS its own type if it is a FlyWire type name, else flywireType, else unmatched
  BANC     the reviewed FlyWire match's cell type (banc_fafb_reviewed_matches), else the BANC
           cell type if it is a FlyWire type name, else unmatched
Output: data/type_matches.csv (type x dataset neuron counts per side) and
        results/matching_coverage.csv (coverage summary incl. the key stimulus/readout types).
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import connectome as C  # noqa: E402
import stimuli as S  # noqa: E402
from paths import DATA, RESULTS, STD  # noqa: E402


def main():
    avail = [d for d in C.DATASETS if (STD / d / "neurons.parquet").exists()]
    fw_types = set(C.load("flywire")[0].type.dropna())
    tabs, cov = [], []
    for d in avail:
        n, _ = C._subgraph(*C.load(d), "brain")
        t = n[n.type.isin(fw_types)].groupby(["type", "side"]).size().unstack(fill_value=0)
        t.columns = [f"{d}_{c}" for c in t.columns]
        tabs.append(t)
        cov.append(dict(dataset=d, brain_neurons=len(n),
                        frac_neurons_with_flywire_type=float(n.type.isin(fw_types).mean()),
                        n_flywire_types_present=int(n.type[n.type.isin(fw_types)].nunique()),
                        **{f"{p}_{s}": len(S.stim_idx(n, p, s)) for p in S.STIM for s in "LR"},
                        **{f"{r}_n": len(S.readout_idx(n, r)) for r in S.READOUTS}))
    tab = pd.concat(tabs, axis=1).fillna(0).astype(int)
    tab["in_all"] = tab.index.isin(C.types_shared())
    tab.to_csv(DATA / "type_matches.csv")
    tab.to_csv(RESULTS / "type_matches.csv")  # small, committed copy
    c = pd.DataFrame(cov)
    c["n_types_shared_all"] = len(C.types_shared())
    c.to_csv(RESULTS / "matching_coverage.csv", index=False)
    print(c.T.to_string())
    print(f"types shared by {avail}: {len(C.types_shared())}")


if __name__ == "__main__":
    main()
