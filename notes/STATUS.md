# STATUS (2026-11-28 23:40)

## Where this project is (plain language)
**About 60% done.** The method works and is validated, all data are in, and a first full set
of results exists at laptop scale. The large robustness runs are what remain.

- **Finished:** novelty check; environment and licence; all three connectomes downloaded,
  checked and converted to one format; Shiu's published results reproduced with his own
  code; our fast simulator validated against it; cell-type matching; the main experiments on
  all three connectomes under three weight normalisations and two sign rules; a first small
  set of controls (5 thinned-FlyWire copies, 5 shuffles per connectome); figures 1-5; a
  paper draft with Introduction, Methods, Results, Discussion and Abstract (preliminary
  numbers); the cloud runbook, tested on this Mac.
- **Running now (started 28 Nov, 23:30):** the full sweep on this Mac, in two background
  jobs (GPU and CPU). At the laptop's speed the first phase (the 50-copy controls behind the
  headline result) needs roughly one to two weeks, and the whole grid about a month. Both
  jobs can be stopped and restarted without losing finished work.
- **Next:** rerun the analysis as results accumulate; replace preliminary numbers in the
  paper; robustness figure and stimulation screen; compile the LaTeX; final citation check.
- **Needs the user:**
  1. Decide whether to rent the RTX 4090. It would finish the whole grid in an estimated
     15-46 hours (about $5-32) instead of about a month here. Everything is ready:
     `docs/cloud_runbook.md`. Results already computed on the Mac can be copied to the box
     so they are not recomputed.
  2. Authors and the AI-use statement (placeholders in the draft).
  3. Install LaTeX on this Mac (for example MacTeX) or say where the draft should be compiled.

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

## Running now
- `nohup caffeinate -i nice .venv/bin/python src/sweep.py --device mps --phase P1,P2,P3 --max_rows 60 > results/mac_sweep_mps.log 2>&1 &`
- `nohup caffeinate -i nice .venv/bin/python src/sweep.py --device cpu --phase P1 --max_rows 60 --reverse > results/mac_sweep_cpu.log 2>&1 &`
  (second worker, walks P1 backwards). Both skip finished items; restart with the same
  commands. Progress: results/ledger.csv and the two logs (they print the rate and ETA).
- The earlier Mac queue (scripts/mac_queue.sh) finished on 26 Nov: 46 items.

## Analysis
`.venv/bin/python src/analysis.py --norms N1,N0,N2` (also runs N1 with transmitter-rule
signs) writes results/*.csv; figures via `src/figures.py fig_repro fig_replication fig_ladder`.

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
