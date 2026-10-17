# TauSpinner Starter

A student tutorial for generating tau pairs, applying TauSpinner spin weights,
and exploring an optional Delphes detector workflow.

**Fresh clone:** follow [installation](docs/installation.md) first. Generated
examples, dependencies and binaries are not included in Git. Paths under
`outputs/` below describe local test results, not downloadable repository files.

**New to generators or tau spin? Start with [the student guide](docs/student_guide.md).**
It explains the physics question, gives commands in order, and suggests a first
small project. The technical details below are reference material, not required
reading on day one. Current qualification limits are in
[the validation roadmap](docs/qualification.md).

Independent local Git repository for **SM elastic gamma gamma -> tau tau**,
with a **Z/gamma* Drell-Yan control**. Nothing here modifies the parent
workspace's gridpacks, samples or benchmark classifications.

## Current tested status

| Stage | Status |
|---|---|
| Independent Git repository | Source and tutorial only; generated data excluded |
| SM elastic MG5/GAMMA-UPC generation | Passed, 1,000 new events |
| DY Pythia + TauSpinner control | Passed, 1,000 decayed events |
| Same-seed CSV/HepMC reproducibility | Passed for DY and photons |
| HepMC weight/daughter read-back | Passed for DY and photons |
| Photon TauSpinner weights | Passed technical smoke test, 1,000 events |
| Delphes detector handoff | 1,000 events pass count, truth-content and event-ID join checks |

**Photon results:** `outputs/photon_smoke/`, including HepMC, weights and plots.
Official 1.1.9 tables are installed unchanged. The photon runtime uses a local
source build with an explicit zero-transverse-momentum coordinate fix, not an
unmodified upstream binary. See [the resolution report](docs/table_resolution.md).
This is technical validation, not physics qualification.

## Intended workflow

1. MG5 + GAMMA-UPC generates stable taus from elastic photons.
2. Pythia decays both taus to pi nu with **uncorrelated, unpolarized** decays
   (`TauDecays:mode=3`, `tauPolarization=0`).
3. TauSpinner calculates an SM spin-correlation weight from the tau and daughter
   four-vectors, including neutrinos. This is not a second event generator.
4. The same events are exported as HepMC2 ASCII, with `unpolarized` and `spin_sm`
   weights, and an event-indexed CSV for analysis and eventual Delphes joining.
5. Truth-level plots compare unpolarized and spin-weighted shapes.

**Status: technical prototype; not yet physics-qualified.** The pinned available
Tauola/TauSpinner release predates the latest photon example API. We compile against
its real photon interface, not a DY substitution. Release-specific photon matrix,
Born versus anomalous-SM convention, and normalization validation remain required.
The Z-like object used internally by the neutral-current TauSpinner entry point
is never inserted into the photon event history.

## Environment and build

```bash
cd tauspinner-starter
source env.sh
cmake -S . -B build
cmake --build build -j2
```

The standalone binary requires Pythia8, HepMC3, LHAPDF, Tauola and TauSpinner.
`env.sh` pins an available LCG108 EL9/gcc13 view and the CVMFS PDF data location.
The photon API must provide `initialize_gamagama`. Older LCG105 TauSpinner is not
an acceptable substitute. A source installation can replace the stack via
`TAUSPIN_STACK`; it must satisfy the same build and validation tests.

The pinned modern package also requires official `table.mu`, `table.down` and
`table.up` files, absent from the installed CVMFS package. Obtain the matching
official TauSpinner EW table/source package and pin its independently checked
SHA-256 (do not invent or synthesize tables):

```bash
python scripts/stage_tables.py /path/to/official-package.tar.gz \
  --sha256 THE_VERIFIED_ARCHIVE_SHA256 --output deps/ew_tables
export TAUSPIN_EW_TABLES="$PWD/deps/ew_tables"
```

The script refuses ambiguous, missing or empty tables. The supplied official
archive has now been verified and staged under `deps/ew_tables_1p1p9`.
Table presence is only a dependency gate, not physics qualification.

For the tested photon runtime, use `source env-photon.sh` and `build/photon`.
On a fresh checkout, stage the archive and run `bash scripts/build_photon_tauola.sh`
first; this builds the documented local coordinate fix. Existing dependency build
directories are deliberately not overwritten.

The official release/mirror lookup and recovery commands are recorded in
[docs/ew_tables.md](docs/ew_tables.md). `scripts/fetch_official_tauola.py`
downloads and inventories the matching release when network access is available;
`build/check-tables` probes actual library loading before event generation.

## Generate elastic events

Use a **configured** MG5 installation containing GAMMA-UPC. The driver copies it
into its own output directory before invoking it, so source installations are
not edited. No existing event sample is reused. For the local MG5 3.5.2 installation,
generation uses its original LCG105/gcc11 environment in a separate subshell:

```bash
( source /cvmfs/sft.cern.ch/lcg/views/LCG_105/x86_64-el9-gcc11-opt/setup.sh
  python scripts/generate.py --mg5 /path/to/mg5_with_gammaUPC \
    --output outputs/elastic_generation --events 1000 --seed 17017 )
bash scripts/smoke_photon.sh outputs/elastic_generation/events.lhe outputs/elastic_spin 1000 27017
```

Generation: 13.6 TeV pp, `lpp1=lpp2=2`, `pdlabel=chff`, alpha(0),
m(tau tau)>50 GeV, tau pT>10 GeV, |tau rapidity|<2.5, DeltaR>0.4.
These are pre-decay hard cuts. No kT, survival variation, dissociation or detector
cut is silently added. Output directories must not already exist.

## Drell-Yan control

One command (new output directory):

```bash
bash scripts/smoke_control.sh outputs/new_control 1000 37017
```

Or run the individual steps:

```bash
source env-control.sh
cmake -S . -B build/control
cmake --build build/control -j2
./build/control/tau-spin dy - outputs/my_dy_control 1000 37017
./build/control/readcheck outputs/my_dy_control/events.hepmc outputs/my_dy_control/weights.csv
python scripts/validate.py outputs/my_dy_control
python scripts/analyze.py outputs/my_dy_control
python -m unittest discover -s tests -v
```

This is a Born-level Pythia Z/gamma* control above 50 GeV without ISR, FSR, MPI
or hadronization. Do not mistake it for a realistic hadronic detector-background
sample. TauSpinner uses NNPDF23_lo_as_0130_qed; matching the generator PDF/EW
settings is an explicit physics-qualification step, not assumed by a smoke test.
The control uses the older LCG105 TauSpinner neutral-current implementation;
it cannot calculate photon spin weights. Use separate shells/build directories
for the two environments. No assertion of equivalence between the two releases
is made.

## Weights and normalization

Input decays have no pair spin correlation. Therefore use
`w_spin_sample = w_input * w_TauSpinner`, **not** its inverse. Do not apply the
same factor again to an already polarized sample. The input production kinematics
and elastic flux remain those of MG5/GAMMA-UPC.

The photon implementation uses a large photon-to-quark mixing factor (1e6),
following the authors' method, and compares 1e9 event by event to measure residual
quark contamination. This is an approximation under validation, not a replacement
of the elastic flux by a photon PDF. No anomalous dipole scan is enabled.

The first workflow forces pi nu for both taus. Plots are **conditional shapes**;
branching fractions have NOT been multiplied into rates. CSV `base_weight` is
the generator weight, not a claim of pb normalization. For an absolute channel
yield one must validate the LHE/Pythia normalization, multiply both branching
fractions, and account for any additional selections. Histogram errors shown
are sumw2, without shared-event covariance or normalization uncertainty.

## Delphes handoff

See [docs/delphes.md](docs/delphes.md). No detector simulation is required for
the initial truth study. Preserve neutrinos in the truth event, even though
they are invisible to Delphes.

## Sources

- [Tauola/TauSpinner releases](https://tauolapp.web.cern.ch/tauolapp/)
- [Photon spin algorithm and usage, Appendix A](https://arxiv.org/abs/2506.15213)
- [TauSpinner algorithm overview](https://arxiv.org/abs/1802.05459)

The installed Pythia `xmldoc/ParticleDecays.xml` specifies mode 3 and polarization
zero. The pinned headers are authoritative for API compilation; the latest paper
uses a different `initialize_GSW` signature. See `docs/validation.md` for tested
scope and unresolved qualification steps.
