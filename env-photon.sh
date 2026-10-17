#!/usr/bin/env bash
# Isolated numerical collinear fix, never changes the CVMFS installation.
_tau_repo=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "${_tau_repo}/env.sh"
export TAUOLA_ROOT="${_tau_repo}/deps/tauola_collinear_fix/install"
export TAUSPIN_EW_TABLES="${_tau_repo}/deps/ew_tables_1p1p9"
export LD_LIBRARY_PATH="${TAUOLA_ROOT}/lib:${LD_LIBRARY_PATH:-}"
unset _tau_repo
