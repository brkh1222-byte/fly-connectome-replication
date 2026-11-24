# Data access (T1.1-T1.3), checked 2026-11-24

All files are public, need no login and are CC BY 4.0 unless noted. Download scripts:
`src/get_flywire.py`, `src/get_banc.py`, `src/get_male_cns.py`. They resume from `.part`
files and skip finished ones. Files go to `$FLY_DATA/raw/` (default `data/raw/`, git-ignored).

## FlyWire v783 (female brain): Dorkenwald et al. 2024; Schlegel et al. 2024
| File | Source | Size | Used for |
|---|---|---|---|
| `Connectivity_783.parquet`, `Completeness_783.csv` (and the v630 pair) | Shiu et al. model repo, github.com/philshiu/Drosophila_brain_model, commit 91bdd1e (MIT) | 96 MB / 3 MB | The FlyWire model graph and signs, exactly as Shiu distributes them |
| `Supplemental_file1_neuron_annotations.tsv` | github.com/flyconnectome/flywire_annotations (Schlegel et al. 2024) | 32 MB | Cell type, side, super class, top_nt |
| `proofread_connections_783.feather` (optional, `--zenodo`) | Zenodo 10.5281/zenodo.10676866 (v783.0, CC BY 4.0) | 852 MB | Derivation check only. It stalled at 100 MB on 24 Nov (Zenodo throttling) and is not needed |

Shiu's v783 table: 138,639 neurons, 15,091,983 edges, 54,492,922 synapses, no threshold.
It is the summed proofread connectivity.

## BANC v888 (female brain + nerve cord): Bates et al. 2026, Nature
Harvard Dataverse doi:10.7910/DVN/7WTH1N, dataset version 3.0, CC BY 4.0. Access goes through
`https://dataverse.harvard.edu/api/access/datafile/<id>`, which redirects (303) to signed S3
URLs. **No login is needed** except for the raw `chunk_*.parquet` files (restricted; not
used). The `.csv.gz` files are served uncompressed with `?format=original`.
| File id | File | Size |
|---|---|---|
| 13994485 | banc_fafb_reviewed_matches.csv.gz (BANC root id → FlyWire 783 root id + type) | 6.6 MB |
| 13994488 | banc_malecns_reviewed_matches.csv.gz | 0.2 MB |
| 13916450 | banc_888_neurotransmitter_prediction_v2.csv | 21 MB |
| 14033740 | banc_888_meta.feather | 58 MB |
| 13992792 | banc_888_edgelist_simple_v2.feather (synapse table v2, the BANC paper's) | 305 MB |
| 13918810 | banc_888_edgelist_simple_v3.feather (optional, `--v3`) | 359 MB |

## Male CNS v1.0 (male brain + nerve cord): Berg et al. 2026, Cell
Public bucket `gs://flyem-male-cns/v1.0/connectome-data/flat-connectome/`, fetched anonymously
over HTTPS (`https://storage.googleapis.com/flyem-male-cns/v1.0/...`), CC BY 4.0.
| File | Size | Notes |
|---|---|---|
| body-annotations-male-cns-v1.0-minconf-0.5.feather | 14.5 MB | type, flywireType, superclass, somaSide/rootSide, status |
| body-neurotransmitters-male-cns-v1.0.feather | 43 MB | predicted_nt per body (plus cell-type consensus) |
| connectome-weights-male-cns-v1.0-minconf-0.5-traced-only.feather | 508 MB | Edges among Traced bodies, synapse confidence ≥ 0.5 (decision D4) |

Other weight tables exist: full at 1.05 GB, and "significant-only" at 502 MB.

## Practical notes
- On 24 Nov 2026 the machine's shared bandwidth was 10-140 KB/s, so downloads took hours.
  On a cloud box they should take minutes.
- FlyWire's `side` labels are from the fly's perspective. Shiu's "right" neuron lists are on
  FlyWire side `left`.
