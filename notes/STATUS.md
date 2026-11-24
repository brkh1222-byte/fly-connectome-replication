# STATUS (checkpoint 2026-11-25 01:15)

## Done
- Novelty: heavy partial overlap with cerebro-mosca (FlyWire vs BANC). Precise comparison and
  framing in notes/novelty.md; decisions D1-revised and D6-D9 in notes/decisions.md.
- Env, licence (MIT), download scripts, data access notes (notes/data_access.md).
- **All data downloaded and checksum-verified** (data/raw, git-ignored):
  - FlyWire: Shiu repo files + Schlegel annotations.
  - Male CNS v1.0: traced-only weights, annotations, NT.
  - BANC v888: meta + NT (Dataverse, MD5 OK); edgelist_simple_v2 (GCS mirror, MD5 = Dataverse).
- Standardised all three (data/std): flywire 138,639 neurons / 15.09 M edges / 54.5 M synapses;
  banc 150,802 / 11.18 M / 34.4 M (brain 126,389); malecns 165,122 / 25.56 M / 124.0 M (brain
  144,717). 6,531 cell types are shared by all three. Per-type input vs FlyWire: BANC 0.448×,
  male CNS 1.755× (results/dataset_summary.csv, type_input_comparison.csv,
  matching_coverage.csv).
- **Validation (results/gpu_validation.md): PyTorch float32 vs Brian2 float64 passes on MPS 3/3;
  CPU 1/1 run** (other CPU runs were stopped because of machine overload). Fig:
  paper/figures/fig2_validation.*
- Brian2 reproduction (src/repro_shiu.py): partially run (results/brian2/, about 6/37 runs).
  It resumes from finished files.
- Pipeline code: connectome.py (N0/N1/N2, thresholds, signs, shuffle/degrade/edgenoise),
  stimuli.py, experiments.py (ledger), agreement.py, analysis.py, summary.py, match_types.py,
  sweep.py (full grid), figures.py.
- Cloud runbook: docs/cloud_runbook.md, scripts/cloud_bootstrap.sh, scripts/run_sweeps.sh.
  **Self-tested on CPU with the tiny grid: PASS, resume verified.** Estimate for one 4090:
  15-46 h (central about 28 h), $5-32. torch.compile-fused update is on by default for CUDA.
- Paper: paper/main.tex with intro + methods drafted; references.bib (27 entries, verified).

## Compute reality on this Mac
Shared with other agents (load average 12-31 on 10 cores; another job also uses MPS).
Benchmark (FlyWire core battery, 50 ms runs, under load):
- MPS: 60 rows → 21 ms/step = 3.5 s per trial-second; 360 rows → 204 ms/step = 5.7 s per trial-second.
- CPU: 60 rows → 50 ms/step = 8.3 s per trial-second.
So MPS works best with small batches (`--max_rows 60`). One core battery
(12 exps × 30 trials × 1 s) takes about 21 min per variant on MPS under load.

## Running now (detached with nohup; both resumable, so just re-run the same command)
- Main runs (MPS): `nohup bash scripts/mac_main.sh main > results/mac_main.log &`
  (`main` = experiments.MAIN = flywire/banc/malecns × {N1, N0, N2} own signs + N1 nt signs; the
  currently running job uses the same 12 variants as explicit JSON). Batteries core then
  core_rep. Outputs go to
  results/runs/*/core*.npz and results/ledger.csv. About 20-30 min per variant-battery under
  load, so about 10-12 h in total.
- Brian2 reproduction: `nohup caffeinate -i nice .venv/bin/python src/repro_shiu.py > results/repro_shiu.log &`

## Next steps
1. When main runs land: `python src/analysis.py` → results/replication_table.csv,
   agreement_ladder.csv, agreement_summary.csv. Then figures (src/figures.py) and paper results.
2. Degraded-FlyWire and shuffle copies: a few on the Mac
   (`src/experiments.py --variants degrade --n 5`), the full set on the 4090.
3. When the researcher provides SSH details: clone the repo on the box and run
   `bash scripts/run_sweeps.sh`; rsync results back (docs/cloud_runbook.md §2).
4. Fill paper/sections/results.tex, discussion, abstract; paper/notes.md with sources.
