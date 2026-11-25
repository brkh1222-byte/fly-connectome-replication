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

## Brian2 reproduction of Shiu et al. (final; 30 trials × 1 s each; results/repro_shiu.csv)
| Number | Value |
|---|---|
| Sugar GRNs (Shiu's list) → MN9, v783, 40 / 100 / 200 Hz | 3.4 / 61.3 / 89.1 Hz |
| Same, v630 (as published) | 5.4 / 67.7 / 94.0 Hz |
| Sugar 100 Hz + bitter 0 / 50 / 100 / 200 Hz → MN9 (v783) | 61.8 / 33.7 / 3.6 / 0.03 Hz |
| Water GRNs 100 / 200 / 260 Hz → MN9 (v783) | 0.0 / 31.7 / 52.0 Hz |
| JO-CE vs JO-F → aBN1 at 100 / 160 / 220 Hz (v783) | 25.8 vs 0.9 / 55.6 vs 1.3 / 73.5 vs 4.8 Hz |
Not compared numerically with Shiu's published curves (their raw outputs were not downloaded);
the qualitative results match their Figs 1, 3, 4, 5.

## PRELIMINARY Mac-scale results (30 trials × 1 s; 3 degraded copies, 3 shuffles; to be superseded)
| Number | Value | Source |
|---|---|---|
| FlyWire L, 150 Hz: sugar→MN9 / bitter suppression / JO-CE→aBN1 / JO-F→aBN1 | 72.1 Hz / 85% / 34.1 Hz / 0.1 Hz | results/replication_table.csv, activity_table.csv |
| FlyWire R sugar: MN9, active neurons | 1.4 Hz, about 8,465 | results/activity_table.csv |
| BANC N0: all readouts | 0 Hz | results/replication_table.csv |
| BANC N1: sugar→MN9 L / R; JO-CE→aBN1 L (active) | 0 / 2.6 Hz; 22.5 Hz (13,143) | replication_table.csv, activity_table.csv |
| N1 scale factors BANC / male CNS | 199/92 = 2.16; 199/326 = 0.61 | results/dataset_summary.csv (median_input_anchor) |
| Male CNS N0: sugar→MN9 L/R; JO-CE→aBN1 L/R | 72.6 / 71.1; 98.9 / 62.9 Hz | replication_table.csv |
| Male CNS N1: sugar→MN9 L/R; JO-CE→aBN1 L/R | 5.7 / 30.5; 84.7 / 56.4 Hz | replication_table.csv |
| Shuffles: MN9, aBN1 | 0 Hz in all (3 per connectome, N1) | results/control_readouts.csv |
| Ladder medians N1: FW–BANC / FW–mCNS / BANC–mCNS | 0.21 / 0.10 / 0.03 | results/agreement_summary.csv |
| Ladder medians N0: same pairs | 0.20 / 0.03 / 0.04 | agreement_summary.csv |
| Hemisphere medians: FlyWire; male CNS N1/N0; BANC N1/N0 | 0.35; 0.52/0.77; 0.07/0.32 | agreement_summary.csv |
| Shuffle rung medians N1 (FW / BANC / mCNS) | −0.42 / −0.42 / −0.12 | agreement_summary.csv |
| Experiments with >2% neurons active, N1 own signs | 11 of 36 | results/activity_table.csv |
| No-runaway medians N1: FW–BANC / FW–mCNS / FW hemispheres | 0.21 / 0.18 / 0.48 | results/agreement_summary_no_runaway.csv |
| Degraded FlyWire N0: sugar→MN9; JO-CE→aBN1 | 0 Hz (3/3); 14.3 Hz | results/control_readouts.csv |
| Degraded FlyWire N1: sugar→MN9 | 69.1 Hz (63.0–72.4) | control_readouts.csv |
| FlyWire vs degraded copies, median ρ, N0 / N1 | 0.55 / 0.49 | agreement_summary.csv |
| FW–BANC ρ below degraded range: N0 / N1 | 9 of 9 / 7 of 9 protocol-sides | results/completeness_test.csv |
