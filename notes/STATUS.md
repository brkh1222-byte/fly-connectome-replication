# STATUS (checkpoint 2026-11-24 ~16:05, before Mac shutdown)

## Done
- Novelty check: heavy partial overlap (cerebro-mosca Zenodo 10.5281/zenodo.23005090; brainlab), NOT a scoop.
  See notes/novelty.md, decision D1 in notes/decisions.md (continue; headline = male CNS rung + nulls +
  degraded-FlyWire completeness control + pre-specified sweep).
- uv env `.venv` (py3.11; brian2 2.9.0, numpy 2.2.6 pinned, torch 2.15.0). requirements.lock committed.
- Licence MIT (notes/licence.md). Authorship rule updated in CLAUDE.md/TASKS.md.
- Brian2 semantics measured (notes/brian2_semantics.md): input during refractory is DISCARDED.
- src/shiu_brian2.py (reference; ~4.3 s/trial cython, 2.2 GB RAM). Sugar 100 Hz v783: MN9 ~62 Hz.
- src/lif_torch.py event-driven float32 LIF. Benchmark (old single-exp version, 30 trials, sugar):
  CPU 199 s, MPS 97 s (identical counts CPU vs MPS with same CPU RNG).
- Just refactored lif_torch.py to `run_batch` (many experiments per batch, device RNG). UNTESTED.

## In progress (killed at shutdown; all resumable)
- src/validate.py --devices mps,cpu (Brian2 vs Torch, 3 exps x 30 trials). Brian2 outputs cached in
  results/validation/ (if present they are reused). Torch .npy there came from the OLD lif_torch:
  DELETE results/validation/torch-* before re-running so the new code is validated.
- Downloads (resumable via .part files; scripts skip finished files):
    nice .venv/bin/python src/get_banc.py        # BANC v888 (Dataverse, slow ~80 KB/s)
    nice .venv/bin/python src/get_male_cns.py    # male CNS v1.0 traced-only weights + NT
  FlyWire annotations are done. Zenodo FlyWire file is optional (`src/get_flywire.py --zenodo`).
  NOTE: _download.fetch resumes .part with a Range header.

## Key findings so far
- Shiu "right" sets = FlyWire side 'left'. Shiu sugarR = LB3c(9)+LB3d(5)+LB4b(4)+LB3b(2); waterR = LB3a(11)+LB3c(7);
  bitterR = LB1a-d; JO_CE = JO-C*/JO-E*; JO_F = JO-F*. MN9 = FlyWire type CB0701 (male CNS type MN9,
  flywireType CB0701); aBN1 = SAD093 in both.
- Male CNS annotations use FlyWire names (flywireType); LB*/JO-* types present.
- Shiu v783 graph: 138,639 neurons, 15.09M edges, 54.5M synapses, unthresholded; signs mostly top_nt rule
  (ACh/DA/OA/5HT +, GABA/Glu -) with ~6k disagreements -> FlyWire uses Shiu signs; others own NT rule.

## Next steps
1. Test run_batch (quick 2-trial sanity vs old numbers: sugar 100 Hz MN9 ~60 Hz, ~350 active), then
   `rm results/validation/torch-*; caffeinate -i nice .venv/bin/python src/validate.py --devices mps,cpu`.
2. Finish downloads; write src/standardise.py (neurons/edges parquet, brain-only + CNS), match_types.py
   (type-based stimulus sets: sugar=LB3b+LB3c, bitter=LB1a-d, water=LB3a, JO-CE, JO-F; readouts MN9/CB0701, SAD093).
3. experiments.py / agreement.py / nulls.py / degrade.py; main runs on Mac (MPS).
4. Cloud runbook for RTX 4090 (float32): docs/cloud_runbook.md, scripts/cloud_bootstrap.sh, scripts/run_sweeps.sh;
   test locally on tiny grid; estimate 4090 hours and cost. Do NOT rent anything.
5. Figures, paper/main.tex, paper/notes.md.
