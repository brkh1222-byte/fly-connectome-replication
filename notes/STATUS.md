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

## Running now (2026-11-25 10:30)
- `nohup bash scripts/mac_queue.sh > results/mac_queue.log 2>&1 &` (MPS; resumable). Done:
  main N1 and N0 core (all three), degrade→BANC seeds 0-2 (N0, N1), shuffles seeds 0-2 (N1).
  Now: core_rep N1 (seed rung), then core_bal (D10), nt signs, N2, seeds 3-4, core_rep N0.
- CPU worker finished (seeds 1, 2). Brian2 reproduction finished (T2.1 done).

## Preliminary analysis DONE (commits 5172f74, 119b082)
`.venv/bin/python src/analysis.py --norms N1,N0` writes replication_table.csv,
agreement_ladder.csv, agreement_summary*.csv, completeness_test.csv, control_readouts.csv,
activity_table.csv. Figures: `src/figures.py fig_repro fig_replication fig_ladder`.
Paper: results, discussion, abstract filled with preliminary numbers (paper/notes.md lists
each with its source). Remaining todo items are the full-grid parts and the seed /
balanced-hemisphere / nt-sign rungs (rerun analysis when the queue finishes them).
Headline so far: degraded FlyWire loses sugar→MN9 like BANC (N0), but N1 rescues degraded
FlyWire and not BANC, and FlyWire-BANC rho is below the degraded range: "partly explained".

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
