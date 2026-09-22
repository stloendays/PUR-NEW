#!/usr/bin/env bash
# Drive the two primary Agent V5 arms INTERLEAVED: one V5_NO_GATE run, then one V5_FULL
# run, ten times. Each arm keeps its own frozen series contract with N declared before its
# first run; interleaving only changes the order in which the declared runs are executed.
#
# Running one arm to completion and then the other would confound arm with wall-clock time,
# because the model endpoint can drift across an hour. Alternating removes that confound.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PY:-/d/Tools/pur_bridge_env/Scripts/python.exe}"
ENV_FILE="${ENV_FILE:-/d/Research/PUR-Essay/.env}"
N="${N:-10}"

NO_GATE_DIR="$ROOT/results/agent_v5/series_no_gate_n${N}"
FULL_DIR="$ROOT/results/agent_v5/series_full_n${N}"

run_chunk() {
  local arm="$1" out="$2" resume="$3"
  local args=(--arm "$arm" --env-file "$ENV_FILE" --n-runs "$N" --output-dir "$out" --max-new-runs 1)
  if [ "$resume" = "resume" ]; then args+=(--resume); fi
  "$PY" "$ROOT/scripts/run_agent_v5_series.py" "${args[@]}"
}

for i in $(seq 1 "$N"); do
  if [ "$i" -eq 1 ]; then mode="fresh"; else mode="resume"; fi
  echo "=== interleaved block $i/$N ==="
  run_chunk V5_NO_GATE "$NO_GATE_DIR" "$mode"
  run_chunk V5_FULL "$FULL_DIR" "$mode"
done

echo "=== both arms finished; producing the cross-arm comparison ==="
"$PY" "$ROOT/scripts/run_agent_v5_comparison.py" \
  --no-gate-series "$NO_GATE_DIR" \
  --full-series "$FULL_DIR" \
  --output-dir "$ROOT/results/agent_v5/comparison_n${N}"
