#!/usr/bin/env bash
# Run from anywhere; creates a NEW directory, never replaces previous runs.
set -eo pipefail
cd "$(dirname "$0")/.."
source env-control.sh
set -u
output=${1:-outputs/control_smoke}
events=${2:-1000}
seed=${3:-37017}
if [[ -e "$output" || -e "${output}.log" ]]; then
  echo "Refusing to overwrite existing output" >&2
  exit 1
fi
mkdir -p "$(dirname "$output")"
cmake -S . -B build/control
cmake --build build/control -j2
python -m unittest discover -s tests -v
./build/control/tau-spin dy - "$output" "$events" "$seed" > "${output}.log" 2>&1
./build/control/readcheck "$output/events.hepmc" "$output/weights.csv"
python scripts/validate.py "$output"
python scripts/analyze.py "$output"
python scripts/provenance.py --binary build/control/tau-spin --output "$output/build_manifest.json"
