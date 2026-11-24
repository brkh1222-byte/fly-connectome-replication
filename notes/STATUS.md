# STATUS (checkpoint 2026-11-25 00:45)

## Done
- Novelty: heavy partial overlap with cerebro-mosca (FlyWire vs BANC). Precise comparison and
  framing in notes/novelty.md; decisions D1-revised and D6-D9 in notes/decisions.md.
- Env, licence (MIT), download scripts, data access notes (notes/data_access.md).
- **All data downloaded and checksum-verified** (data/raw, git-ignored):
  - FlyWire: Shiu repo files + Schlegel annotations.
  - Male CNS v1.0: traced-only weights, annotations, NT.
  - BANC v888: meta + NT (Dataverse, MD5 OK); edgelist_simple_v2 (GCS mirror, MD5 = Dataverse).
- Standardised: flywire (138,639 neurons / 15.09 M edges / 54.5 M synapses); malecns (165,122 /
  25.56 M / 124.0 M; brain 144,717). Male CNS types harmonised to FlyWire names (95% of brain
  neurons). BANC: TODO (standardise.py banc() not written yet).
- **Validation (results/gpu_validation.md): PyTorch float32 vs Brian2 float64 passes on MPS 3/3;
  CPU 1/1 run** (other CPU runs were stopped because of machine overload). Fig:
  paper/figures/fig2_validation.*
- Brian2 reproduction (src/repro_shiu.py): partially run (results/brian2/, about 6/37 runs).
  It resumes from finished files.
- Pipeline code: connectome.py (N0/N1/N2, thresholds, signs, shuffle/degrade/edgenoise),
  stimuli.py, experiments.py (ledger), agreement.py, analysis.py, summary.py, match_types.py,
  sweep.py (full grid), figures.py.
- Cloud runbook draft: docs/cloud_runbook.md, scripts/cloud_bootstrap.sh, scripts/run_sweeps.sh
  (not yet self-tested).
- Paper: paper/main.tex with intro + methods drafted; references.bib (27 entries, verified).

## Compute reality on this Mac
Shared with other agents (load average 12-31 on 10 cores; another job also uses MPS).
Benchmark (FlyWire core battery, 50 ms runs, under load):
- MPS: 60 rows → 21 ms/step = 3.5 s per trial-second; 360 rows → 204 ms/step = 5.7 s per trial-second.
- CPU: 60 rows → 50 ms/step = 8.3 s per trial-second.
So MPS works best with small batches (`--max_rows 60`). One core battery
(12 exps × 30 trials × 1 s) takes about 21 min per variant on MPS under load.

## Next steps
1. `python src/standardise.py banc` (write banc()); then summary.py and match_types.py.
2. Main runs on MPS, max_rows 60, in priority order:
   `src/experiments.py --variants main --battery core --device mps --max_rows 60`, then core_rep.
3. analysis.py → replication table + ladder; degraded/shuffle (a few copies on the Mac; full set on the 4090).
4. Runbook self-test: `DEVICE=cpu TINY=1 VOL=<scratch> FLY_DATA=$PWD/data bash scripts/run_sweeps.sh --foreground`.
5. Estimate 4090 hours and cost; figures; fill paper results; paper/notes.md.
