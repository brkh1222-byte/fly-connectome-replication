# Paper numbers and their sources

Every number used in `paper/` is listed here with the file that produced it. Mac-scale
results are marked PRELIMINARY: they will be replaced by the full grid (`src/sweep.py`).

## Validation (final for the Mac; CUDA row pending)
| Number | Value | Source |
|---|---|---|
| r(PyTorch, Brian2), MPS, 3 experiments | 0.9994, 0.9997, 0.9994 | results/gpu_validation.csv |
| r(Brian2, Brian2) seed ceiling | 0.9997, 0.9996, 0.9995 | results/gpu_validation.csv |
| sugar→MN9 at 100 Hz, PyTorch vs Brian2 | 62.7 vs 61.4 Hz | results/gpu_validation.csv |
| sugar+bitter→MN9 | 2.9 vs 3.5 Hz | results/gpu_validation.csv |
| JO-CE→aBN1 at 100 Hz | 26.2 vs 25.9 Hz | results/gpu_validation.csv |
| CPU float32, sugar | r = 0.9997, PASS (1 of 3 experiments run) | results/gpu_validation.csv |

## Datasets (final)
| Number | Value | Source |
|---|---|---|
| Brain neurons FlyWire / BANC / male CNS | 138,639 / 126,389 / 144,717 | results/dataset_summary.csv |
| Brain synapses | 54.49 M / 23.26 M / 101.08 M | results/dataset_summary.csv |
| Whole-CNS neurons BANC / male CNS | 150,802 / 165,122 | results/dataset_summary.csv |
| Shared cell types (all three) | 6,531 | results/matching_coverage.csv |
| Neurons with a FlyWire type, BANC / male CNS | 91.7% / 94.9% | results/matching_coverage.csv |
| Per-type input ratio to FlyWire, BANC | 0.448 (IQR 0.325–0.620) | src/summary.py output; results/type_input_comparison.csv |
| Per-type input ratio to FlyWire, male CNS | 1.755 (IQR 1.403–2.271) | same |
| MN9 mean input synapses FlyWire / BANC / male CNS | 5,732 / 2,276 / 3,284 | results/dataset_summary.csv |
| aBN1 mean input synapses | 1,146 / 518 / 3,434 | results/dataset_summary.csv |
| BANC stimulus counts L/R: water 3/15, JO-F 37/108, sugar 32/45 | | results/matching_coverage.csv |

## Prior-work numbers quoted (not ours)
| Number | Source |
|---|---|
| ρ = 0.98 / 0.54 / ≤ 0.32 (seed / hemisphere / FlyWire–BANC); 2.1× fewer synapses | Silva Santos 2026, draft preprint in github.com/amthedev/cerebro-mosca (Zenodo 10.5281/zenodo.23005090) |
| 76.7 / 68.9 / 17.8 Hz sugar→MN9 | Pronexsteam/brainlab README (as read by the helper agent, 24 Nov 2026) |
| 91% of 164 predictions | Shiu et al. 2024 |

## Brian2 reproduction, replication table, ladder, controls
(Filled below as runs finish.)
