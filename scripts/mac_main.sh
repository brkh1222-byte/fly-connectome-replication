#!/usr/bin/env bash
# Main cross-connectome runs on the Mac (MPS), resumable. Usage: bash scripts/mac_main.sh "<json variants>"
cd "$(dirname "$0")/.."
V="$1"
for B in core core_rep; do
  caffeinate -i nice .venv/bin/python src/experiments.py --variants "$V" --battery $B --device mps --max_rows 60
done
