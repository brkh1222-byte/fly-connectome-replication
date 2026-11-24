#!/usr/bin/env bash
# Mac-scale preliminary queue (one MPS job at a time; resumable: finished items are skipped).
# Waits for the first six main "core" items of an already running mac_main.sh job, stops that
# job, then runs the preliminary nulls/controls in priority order and finally the remaining
# main variants. The full grid (src/sweep.py) supersedes all of this.
cd "$(dirname "$0")/.."
PY=".venv/bin/python"
run() { caffeinate -i nice $PY src/experiments.py --variants "$1" --battery "$2" --device mps --max_rows 60; }
if pgrep -f "scripts/mac_main.sh" >/dev/null; then
  until [ "$(grep -c ',core,' results/ledger.csv 2>/dev/null || echo 0)" -ge 6 ] || ! pgrep -f "scripts/mac_main.sh" >/dev/null; do sleep 30; done
  pkill -f "scripts/mac_main.sh"; pkill -f "src/experiments.py"; sleep 3
fi
D='{"dataset":"flywire","norm":"%s","perturb":{"kind":"degrade","seed":%d,"ref":"banc"}}'
S='{"dataset":"%s","norm":"N1","perturb":{"kind":"shuffle","seed":%d}}'
M='[{"dataset":"flywire","norm":"%s"},{"dataset":"banc","norm":"%s"},{"dataset":"malecns","norm":"%s"}]'
run "$(printf "$M" N1 N1 N1)" core
run "$(printf "$M" N0 N0 N0)" core
for k in 0 1 2; do
  run "[$(printf "$D" N0 $k),$(printf "$D" N1 $k)]" core
  run "[$(printf "$S" flywire $k),$(printf "$S" banc $k),$(printf "$S" malecns $k)]" core
done
run "$(printf "$M" N1 N1 N1)" core_rep
run "$(printf "$M" N1 N1 N1)" core_bal
run '[{"dataset":"flywire","norm":"N1","sign":"nt"},{"dataset":"banc","norm":"N1","sign":"nt"},{"dataset":"malecns","norm":"N1","sign":"nt"}]' core
run "$(printf "$M" N2 N2 N2)" core
for k in 3 4; do
  run "[$(printf "$D" N0 $k),$(printf "$D" N1 $k)]" core
  run "[$(printf "$S" flywire $k),$(printf "$S" banc $k),$(printf "$S" malecns $k)]" core
done
run "$(printf "$M" N0 N0 N0)" core_rep
echo QUEUE_DONE
