# TASKS: fly-connectome-replication

Work top to bottom. Tick boxes as tasks complete. Read PROPOSAL.md and CLAUDE.md first.

> **Where things run:** cloud agents write and test code on CPU with small settings (short simulations, few trials). Big sweeps run on the **H100 machine**. Every script takes `--device cuda|cpu`.

## Phase 0: Setup
- [x] **T0.1** Create the environment (done with uv: requirements.txt/requirements.lock instead of `environment.yml`): python 3.11, brian2, torch (CUDA), numpy, scipy, pandas, pyarrow, matplotlib, seaborn and tqdm. Also create `config/default.yaml`.
- [ ] **T0.2 Licence decision.** Choose a repo licence. If code is reused from eonsystemspbc/fly-brain (GPL-2.0+), the repo must be GPL. Otherwise use MIT and reimplement. Shiu's repo is MIT. Record the decision in `notes/licence.md`.

## Phase 1: Data
- [x] **T1.1** Write `src/get_flywire.py` to download FlyWire v783 from Zenodo (10.5281/zenodo.10676866) plus Shiu's repo input files. **Do not use flywire.ai.**
- [x] **T1.2** Write `src/get_male_cns.py` to download male CNS v1.0 weights, annotations and neurotransmitters from `gs://flyem-male-cns/v1.0/`. Use anonymous gsutil or HTTPS.
- [x] **T1.3** Write `src/get_banc.py` to download BANC v888 from Harvard Dataverse (doi:10.7910/DVN/7WTH1N). Record the file list, sizes and any login requirement in `notes/data_access.md`.
- [x] **T1.4** Write `src/standardise.py` to convert all three datasets to a common format: `neurons.parquet` (id, type, side, superclass, neurotransmitter, sign) and `edges.parquet` (pre, post, n_syn). Record summary statistics per dataset (neuron count, edge count, synapse density) in `results/dataset_summary.csv`.

## Phase 2: Reproduce
- [ ] **T2.1** (IN PROGRESS: Brian2 v630/v783 curves, src/repro_shiu.py) Run Shiu's Brian2 model on FlyWire v783: sugar GRN stimulation → MN9.
  *Done when:* MN9 activates as in the paper; the figure is in `results/repro_sugar_mn9.png`.
- [x] **T2.2** Write `src/lif_torch.py`, a batched sparse LIF in PyTorch with the same equations and parameters as Shiu.
  *Done when:* firing rates match Brian2 within seed noise on 3 experiments (`results/gpu_validation.md`).

## Phase 3: Cross-connectome
- [x] **T3.1** Write `src/match_types.py` to build `data/type_matches.csv` linking cell types across FlyWire, BANC and the male CNS. Include the sugar, water and bitter GRNs, MN9 and the grooming neurons. Report coverage.
- [ ] **T3.2** Write `src/experiments.py` to run Shiu's experiments on all three connectomes.
  *Done when:* there is a replication table for each prediction.
- [ ] **T3.3** Write `src/agreement.py`: rank correlation of firing rates over matched types and top-k overlap, for FlyWire–BANC vs FlyWire–male CNS.

## Phase 4: Robustness (H100)
- [ ] **T4.1** (code done: src/sweep.py P2; to run on rented RTX 4090 via docs/cloud_runbook.md) Write `src/sweep.py` covering normalisation (raw / density / input fraction) × synapse threshold × edge-noise bootstrap × seeds.
- [ ] **T4.2** (code done: shuffle + degraded FlyWire, src/sweep.py P1; 4090) Write `src/nulls.py` to build degree-preserving shuffled connectomes and compute the null agreement.
- [ ] **T4.3** (code done: src/sweep.py P3; 4090) Run a stimulation screen over all matched sensory types.
- [ ] **T4.4** Make the figures.

## Phase 5: Write-up
- [ ] **T5.1** Write `paper/notes.md` with bullet results. Claude drafts the full paper (`paper/main.tex`); the researcher reviews and edits it; the paper carries an AI-use disclosure (`[AUTHORS — TBD]`, `[AI-USE STATEMENT — TBD]`).

## Notes (2026-11-25)
- T0.1: uv + Python 3.11 (`requirements.lock`); torch runs on CPU/MPS/CUDA.
- T2.2: float32 PyTorch vs Brian2: MPS 3/3 PASS, CPU 1/1 PASS (results/gpu_validation.md).
- Cloud: runbook self-tested on CPU (docs/cloud_runbook.md). Big sweeps go to a rented RTX 4090.
