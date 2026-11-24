#!/usr/bin/env bash
# Prepare a fresh Ubuntu (22.04/24.04) + NVIDIA driver + CUDA 12 box (RunPod / Vast.ai,
# RTX 4090) that has this repo cloned. Idempotent: safe to re-run.
#   VOL          persistent volume (default /workspace)
#   FLY_DATA     connectome data   (default $VOL/fly_data)
#   FLY_RESULTS  run outputs       (default $VOL/fly_results)
#   DEVICE       cuda (default) | cpu (local self-test)
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VOL="${VOL:-/workspace}"
export FLY_DATA="${FLY_DATA:-$VOL/fly_data}"
export FLY_RESULTS="${FLY_RESULTS:-$VOL/fly_results}"
DEVICE="${DEVICE:-cuda}"
mkdir -p "$FLY_DATA" "$FLY_RESULTS"
cd "$REPO"
log() { echo "[bootstrap $(date +%H:%M:%S)] $*"; }

# 1. system tools (only if missing and we are root)
if [ "$(id -u)" = 0 ] && command -v apt-get >/dev/null; then
  need=""; for t in git rsync gcc tmux curl; do command -v $t >/dev/null || need="$need $t"; done
  [ -n "$need" ] && { log "apt install$need"; apt-get update -qq && apt-get install -y -qq git rsync build-essential tmux curl; }
fi

# 2. uv + Python 3.11 environment (Linux PyPI torch wheels ship with CUDA 12)
export PATH="$HOME/.local/bin:$PATH"
command -v uv >/dev/null || { log "installing uv"; curl -LsSf https://astral.sh/uv/install.sh | sh; }
if [ ! -x .venv/bin/python ]; then
  log "creating venv"; uv venv --python 3.11 .venv
fi
log "installing pinned requirements"
uv pip install --python .venv/bin/python -q -r requirements.lock
PY=.venv/bin/python

# 3. device check
if [ "$DEVICE" = cuda ]; then
  $PY - <<'PYEOF'
import torch
assert torch.cuda.is_available(), "CUDA not available"
p = torch.cuda.get_device_properties(0)
print(f"[bootstrap] GPU {p.name}, {p.total_memory/2**30:.1f} GiB, torch {torch.__version__}, CUDA {torch.version.cuda}")
PYEOF
fi

# 4. data (versioned public releases; resumable)
log "downloading data into $FLY_DATA"
$PY src/get_flywire.py
$PY src/get_banc.py
$PY src/get_male_cns.py
log "standardising"
for d in flywire banc malecns; do
  [ -f "$FLY_DATA/std/$d/edges.parquet" ] || $PY src/standardise.py $d
done
log "bootstrap done"
