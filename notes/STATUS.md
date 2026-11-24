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

## Running now (2026-11-25 03:15; all detached, resumable; restart = same command)
- `nohup bash scripts/mac_queue.sh > results/mac_queue.log 2>&1 &` (MPS; about 43 min per item):
  main N1 core DONE for all three (01:29, 02:11, 02:54); now N0 core; then degrade→BANC
  seed 0 (N0, N1), shuffle seed 0, ..., core_rep, core_bal, nt signs, N2.
- `nohup bash scripts/mac_cpu_worker.sh > results/mac_cpu_worker.log 2>&1 &` (CPU; starts
  when repro_shiu finishes): degrade/shuffle seeds 2 and 1.
- `nohup caffeinate -i nice .venv/bin/python src/repro_shiu.py > results/repro_shiu.log &`
  (30/37 at 03:01).

## Preliminary results so far (N1, own signs; results/replication_table.csv,
## agreement_ladder.csv, agreement_summary*.csv, activity_table.csv)
- FlyWire L: sugar→MN9 72 Hz, bitter suppression 85%, JO-CE→aBN1 34 Hz, water→MN9 0 Hz.
- BANC N1: sugar→MN9 0 Hz (L); JO-CE→aBN1 22 Hz (L) but in a runaway state (13k active).
- Male CNS N1: sugar→MN9 5.7 (L) / 30.5 Hz (R); JO-CE→aBN1 85 / 56 Hz; bitter runaway (9k active).
- Ladder medians: hemisphere FlyWire 0.35, BANC 0.07, male CNS 0.52; FlyWire-BANC 0.21,
  FlyWire-male CNS 0.10, BANC-male CNS 0.03. Runaway states dominate (decision D11).

## Researcher's choices (25 Nov)
Framing (a); rent a 4090 later (no SSH yet; do not wait); Shiu's signs primary. Commit
messages now end with `Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>`.

## Next steps
1. As items land: `.venv/bin/python src/analysis.py --norms N1,N0` → replication_table.csv,
   agreement_ladder.csv, agreement_summary.csv (label PRELIMINARY).
2. Figures: `.venv/bin/python src/figures.py fig_repro fig_replication fig_ladder`
   (fig2_validation and fig3_datasets are done).
3. Fill paper/sections/results.tex (scaffold exists), discussion, abstract; add every number
   to paper/notes.md (started).
4. When SSH details arrive: docs/cloud_runbook.md.
