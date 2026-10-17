#!/usr/bin/env bash
set -eo pipefail
cd "$(dirname "$0")/.."
source env.sh
set -u
root=$PWD
archive=${1:-deps/official_1p1p9_download/TAUOLA.1.1.9-LHC.tar.gz}
expected=4eb69f38bc0163568034f95b47d1ae461becbff9935921d57e49d3583cb3c158
actual=$(sha256sum "$archive")
[[ ${actual%% *} == "$expected" ]] || { echo 'Archive checksum mismatch' >&2; exit 1; }
destination=deps/tauola_collinear_fix
[[ ! -e "$destination" ]] || { echo 'Build directory exists; refusing overwrite' >&2; exit 1; }
mkdir -p "$destination"
tar -xzf "$archive" -C "$destination"
cd "$destination/TAUOLA"
patch --forward -p1 < "$root/patches/particle-collinear.patch"
./configure --prefix="$PWD/../install" --with-pic \
  --with-lhapdf="$TAUSPIN_STACK" --without-hepmc --without-hepmc3 \
  FFLAGS='-O2 -fallow-argument-mismatch' > ../configure.log 2>&1
make -j2 > ../build.log 2>&1
make install > ../install.log 2>&1
