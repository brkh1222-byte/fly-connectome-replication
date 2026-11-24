# Cloud runbook: full sweeps on one rented RTX 4090

This runbook takes a fresh rented GPU box to finished T4.1 (robustness sweep), T4.2 (nulls
and degraded-FlyWire control) and T4.3 (stimulation screen) results with **one command**, then
syncs the results (not the data) back to the Mac.

The simulator runs in **float32** (the 4090 has weak FP64). On the Mac, float32 was validated
against Brian2 (float64) within seed noise: `results/gpu_validation.md`. The box re-runs the
same validation on CUDA as a gate before any sweep starts.

## 0. What to rent
- RunPod or Vast.ai, **1× RTX 4090 (24 GB)**, on-demand. Image: any Ubuntu 22.04/24.04 with an
  NVIDIA driver for CUDA 12, e.g. RunPod "PyTorch 2.x / CUDA 12" or Vast "pytorch/pytorch:*-cuda12*".
- Volume: **≥ 50 GB** mounted at `/workspace`. Data needs about 3 GB, results about 1-2 GB,
  and the environment about 6 GB.
- CPU ≥ 8 vCPU and RAM ≥ 32 GB. Standardising the male CNS peaks at about 6 GB RAM.
- Open SSH and note the host, port and user.

## 1. One command
```bash
git clone https://github.com/brkh1222-byte/fly-connectome-replication.git /workspace/fly-connectome-replication
cd /workspace/fly-connectome-replication && git checkout research-plan
bash scripts/run_sweeps.sh          # starts tmux session "fly" and returns immediately
```
`run_sweeps.sh` does the following:
1. **bootstrap** (`scripts/cloud_bootstrap.sh`): apt tools if missing, `uv`, a Python 3.11
   venv from `requirements.lock` (the Linux PyPI torch wheel bundles CUDA 12), a GPU check, and
   downloads of FlyWire (Shiu repo + annotations), BANC v888 (Dataverse) and male CNS v1.0
   (GCS) into `/workspace/fly_data`, then standardisation.
2. **validation gate**: `src/validate.py --devices cuda`, which compares CUDA float32 with
   the Brian2 reference runs committed in `results/validation/`. If it fails, the script
   stops and the sweep does not run.
3. **sweep**: `src/sweep.py --device cuda` runs phases P1 → P2 → P3 in priority order. Each
   finished item is written atomically to `/workspace/fly_results/runs/<variant>/<battery>.npz`
   and appended to `/workspace/fly_results/ledger.csv`. **Re-running the same command resumes**:
   finished items are skipped. Batch size is chosen automatically to fill about 60% of free
   GPU memory.

Monitor: `tmux attach -t fly`, or `tail -f /workspace/fly_results/sweep.log`, or
`wc -l /workspace/fly_results/ledger.csv`.

To run only some phases: `PHASES=P1 bash scripts/run_sweeps.sh`. To see the plan:
`.venv/bin/python src/sweep.py --list`.

## 2. Sync results back to the Mac (results only, never data)
From the Mac:
```bash
rsync -avz --partial -e "ssh -p <PORT>" <USER>@<HOST>:/workspace/fly_results/ \
      ~/Desktop/fly-connectome-replication/results/cloud/
```
This is safe to repeat during the run. Stop the pod once `sweep.log` shows `=== finished`
and the final rsync has completed.

## 3. The grid (scientifically complete; see notes/decisions.md D6)
| Phase | Task | Content | Items |
|---|---|---|---|
| P1 | T4.2 | Degraded FlyWire to BANC and to male CNS per-type input deficits × {N0, N1} × 50 copies; degree-preserving shuffles × 3 datasets × {N0, N1} × 50 | 500 |
| P2 | T4.1 | 3 datasets × subgraph (brain; + whole CNS for BANC/male CNS) × threshold {1, 3, 5, 10} × norm {N0, N1, N2} × sign {own, nt, type}, each with a replicate seed; + 10 edge-noise bootstraps for every own-sign setting | see `--list` |
| P3 | T4.3 | Every shared sensory type × side at 150 Hz, 3 datasets × {N0, N1}, + 5 shuffled controls per dataset | 21 |

Every item runs Shiu's settings: 30 trials × 1 s per experiment. The "core" battery has 12
experiments: sugar, bitter, water, JO-CE, JO-F and sugar+bitter, each on both sides.

## 4. Time and cost (measured vs extrapolated)
**Grid size** (`src/sweep.py --list`): P1 180,000; P2 345,600; P3 139,860 trial-seconds.
Total **665,460 trial-seconds**, i.e. 1-s simulated trials of the whole network.

**Measured on the Mac** (Apple M4, 10-core GPU, about 120 GB/s; shared with other jobs, load
average 12-31). FlyWire core battery, 500-step runs:
| Backend | rows/batch | ms per 0.1-ms step | s per trial-second |
|---|---|---|---|
| MPS | 60 | 21 | 3.5 |
| MPS | 360 | 204 | 5.7 |
| CPU (float32, 10 cores, shared) | 60 | 50 | 8.3 |
At these rates the full grid would take about 27 days on the Mac MPS backend, which is why it
goes to the cloud.

**Extrapolated for one RTX 4090** (not measured; no CUDA device was available). Per
row-step, the simulation is (i) a dense element-wise update over N ≈ 126k-145k neurons and
(ii) an event-driven scatter of the spikes' outgoing synapses. With the fused (torch.compile)
update, (i) is about 1-2 passes of about 4-8 bytes per neuron: roughly 1-2 µs per row-step at
about 700 GB/s effective bandwidth. (ii) depends on activity. In the core battery a few
hundred to a few thousand neurons are active, i.e. about 1-10 spikes per row-step of about
100-1,000 synapses each, which gives roughly 5-20 µs per row-step in atomic scatter-adds. At
the auto batch size (about 1,000-2,000 rows), fixed per-step overheads (about 0.3-0.5 ms for
kernel launches and two host syncs) add less than 0.5 µs per row-step.
- Estimate: **0.08-0.25 s per trial-second**, central about 0.15 s.
  - That is 15-45× faster than the shared M4; the 4090 has about 8× its memory bandwidth and
    far more parallelism.
- **Full grid: about 15-46 GPU-hours, central about 28 h.**
  - P1 (headline nulls): about 4-12 h.
  - P2: about 8-24 h.
  - P3: about 3-10 h.
- **Cost at $0.35-0.70/h: about $5-32, central about $10-20.**
  - The volume (50 GB at about $0.05-0.10/GB-month) adds under $5.
  - The download and bootstrap take about 15-30 min.

**Calibrate before committing.** `sweep.py` prints wall seconds per trial-second and the phase
ETA after every item. After the first 10-20 P1 items (about 15-30 min), multiply the printed
rate by 665,460 to get the true total. If it is far above the range above, stop the pod and
report the printed rate. Phases are ordered so that a partial run is still useful: P1
contains the headline control.


## 5. Local self-test (done before handing over)
```bash
DEVICE=cpu TINY=1 VOL=/tmp/flytest bash scripts/run_sweeps.sh --foreground
```
This runs the whole chain on CPU with 2 trials × 50 ms and 2 items per phase.

**Self-test result (2026-11-25, Mac, CPU, existing data via `FLY_DATA=$PWD/data`): PASS.**
- Bootstrap ran (env, downloads skipped as already present, standardisation skipped).
- P1 ran a degraded-FlyWire→BANC item and a male CNS shuffle item.
- P2 ran a FlyWire base item and a male CNS whole-CNS / threshold 10 / N2 / type-sign
  core_rep item.
- P3 ran FlyWire and shuffled male CNS stimulation screens of 222 experiments each.
- The run ended with `=== finished`; the ledger had 6 rows and results took 1.6 MB.
- Re-running skipped all items in 10 s (resume works).
- One bug was found and fixed: a name clash in `get_flywire.py`.
- Not tested locally: the CUDA path (no NVIDIA GPU here) and fresh downloads inside the
  script. The downloads were tested separately with the same functions. The fused CUDA
  update path is gated by the CUDA validation step, which must PASS before the sweep starts.
