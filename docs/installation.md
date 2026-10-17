# Set up a fresh clone

## What you need

The tested environment is Linux EL9 with CERN CVMFS. This is not currently a
one-command installation for Windows or macOS. Ask your supervisor for a Linux
machine with the LCG105 and LCG108 views used in the `env*.sh` files.
You need Git, network access for the official archive, disk space, and a compiler.
No generated events, ROOT files or third-party packages are shipped in this repo.

```bash
git clone https://github.com/De-Cristo/tauspinner-starter.git
cd tauspinner-starter
```

## Easiest first exercise: the control sample

```bash
bash scripts/smoke_control.sh outputs/my_control 1000 37017
```

This needs the pinned CVMFS environment but no MG5 input or photon tables.
Look in `outputs/my_control/plots/`. The output directory must not exist already.

## Prepare the photon dependencies

Use the official archive, not replacement tables from an unrelated release:

```bash
python3 scripts/fetch_official_tauola.py --output deps/official_1p1p9_download
python3 scripts/stage_tables.py deps/official_1p1p9_download/TAUOLA.1.1.9-LHC.tar.gz \
  --sha256 4eb69f38bc0163568034f95b47d1ae461becbff9935921d57e49d3583cb3c158 \
  --table-prefix TAUOLA/TauSpinner/examples/Dizet-example \
  --output deps/ew_tables_1p1p9
bash scripts/build_photon_tauola.sh
```

If downloads are blocked, obtain that archive through the official release page
and place it at the shown path. Never bypass a checksum mismatch. This checksum
pins the tested download; it is not a publisher signature.
The build includes a documented coordinate-limit fix; see `table_resolution.md`.
Third-party software retains its own licensing terms and is not redistributed here.

## Generate your photon input

You need a configured MG5 3.5.2 installation with GAMMA-UPC and its elastic chff
flux. This repository does not install that integration. Ask your supervisor for
its path; plain MG5 or a generic photon PDF is not a substitute.

```bash
(
  source /cvmfs/sft.cern.ch/lcg/views/LCG_105/x86_64-el9-gcc11-opt/setup.sh
  python scripts/generate.py --mg5 /path/to/configured/mg5 \
    --output outputs/elastic_generation --events 1000 --seed 17017
)
bash scripts/smoke_photon.sh outputs/elastic_generation/events.lhe outputs/my_photon_run 1000 27017
```

The generator driver makes a local copy before running. This can take time and
disk space. Keep the generation log if anything fails. Do not substitute the DY
control for photon events while calling it a photon study.

## Optional detector exercise and tests

```bash
source env-photon.sh
python scripts/delphes_smoke.py outputs/my_photon_run outputs/my_detector
python scripts/check_qed.py outputs/my_qed_check.json
python -m unittest discover -s tests -v
```

Continue with [the student guide](student_guide.md). The tutorial supports
learning and exploratory shapes; see [qualification](qualification.md) before
making quantitative physics claims.
