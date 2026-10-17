#!/usr/bin/env bash
set -eo pipefail
cd "$(dirname "$0")/.."
source env-photon.sh
set -u
input=${1:-outputs/elastic_generation/events.lhe}
output=${2:-outputs/photon_smoke}
events=${3:-1000}
seed=${4:-27017}
[[ ! -e "$output" && ! -e "${output}.log" ]] || { echo 'Output exists' >&2; exit 1; }
mkdir -p "$(dirname "$output")"
cmake -S . -B build/photon
cmake --build build/photon -j2
./build/photon/check-collinear
./build/photon/check-tables "$TAUSPIN_EW_TABLES"
./build/photon/tau-spin gg "$input" "$output" "$events" "$seed" > "${output}.log" 2>&1
./build/photon/readcheck "$output/events.hepmc" "$output/weights.csv"
python scripts/validate.py "$output"
python scripts/analyze.py "$output"
python scripts/provenance.py --binary build/photon/tau-spin --output "$output/build_manifest.json"
