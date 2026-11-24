#!/usr/bin/env bash
# Second (CPU) worker for the preliminary nulls (D12). Waits for the Brian2 reproduction to
# finish, then runs degrade/shuffle seeds 2 and 1. Resumable.
cd "$(dirname "$0")/.."
while pgrep -f "src/repro_shiu.py" >/dev/null; do sleep 60; done
run() { caffeinate -i nice .venv/bin/python src/experiments.py --variants "$1" --battery core --device cpu --max_rows 60; }
D='{"dataset":"flywire","norm":"%s","perturb":{"kind":"degrade","seed":%d,"ref":"banc"}}'
S='{"dataset":"%s","norm":"N1","perturb":{"kind":"shuffle","seed":%d}}'
for k in 2 1; do
  run "[$(printf "$D" N1 $k),$(printf "$D" N0 $k)]"
  run "[$(printf "$S" flywire $k),$(printf "$S" banc $k),$(printf "$S" malecns $k)]"
done
echo CPU_WORKER_DONE
