#!/usr/bin/env bash
# One command from a fresh CUDA box with the repo cloned to the full T4.1 sweep, T4.2 nulls
# and T4.3 stimulation screen:
#     bash scripts/run_sweeps.sh            # runs inside tmux session "fly" and returns
#     tmux attach -t fly                    # watch;  tail -f $FLY_RESULTS/sweep.log
# Steps: bootstrap (env + data) -> validation gate (float32 CUDA vs Brian2) -> sweep P1,P2,P3.
# Everything is resumable: re-running skips finished items (results/runs/*/*.npz + ledger.csv).
# Local self-test:  DEVICE=cpu TINY=1 VOL=/tmp/flytest bash scripts/run_sweeps.sh --foreground
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VOL="${VOL:-/workspace}"
export FLY_DATA="${FLY_DATA:-$VOL/fly_data}"
export FLY_RESULTS="${FLY_RESULTS:-$VOL/fly_results}"
export DEVICE="${DEVICE:-cuda}"
TINY="${TINY:-0}"
PHASES="${PHASES:-P1,P2,P3}"
mkdir -p "$FLY_RESULTS"
LOG="$FLY_RESULTS/sweep.log"

if [ "${1:-}" != "--foreground" ] && command -v tmux >/dev/null && [ -z "${TMUX:-}" ]; then
  tmux new-session -d -s fly "bash '$REPO/scripts/run_sweeps.sh' --foreground"
  echo "started in tmux session 'fly'; log: $LOG"
  exit 0
fi

cd "$REPO"
{
  echo "=== run_sweeps $(date) device=$DEVICE tiny=$TINY phases=$PHASES"
  bash scripts/cloud_bootstrap.sh
  PY=.venv/bin/python
  if [ "$TINY" = 1 ]; then
    $PY src/sweep.py --device "$DEVICE" --phase "$PHASES" --tiny
  else
    echo "--- validation gate"
    $PY src/validate.py --devices "$DEVICE"
    grep -q "Overall: PASS" results/gpu_validation_${DEVICE}.md || { echo "VALIDATION FAILED - stopping"; exit 1; }
    cp results/gpu_validation_${DEVICE}.* "$FLY_RESULTS/" || true
    $PY src/sweep.py --list --phase "$PHASES"
    $PY src/sweep.py --device "$DEVICE" --phase "$PHASES"
  fi
  echo "=== finished $(date)"
} 2>&1 | tee -a "$LOG"
