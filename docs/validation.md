# Validation status (2026-10-16)

## Superseding status (2026-10-17)

Official-table acquisition, loading, photon execution and repeatability now
pass. See [table_resolution.md](table_resolution.md) for the current results
and the explicitly patched local runtime. The blocked statements and checklist
below describe the earlier investigation, not the current dependency state.
Full physics qualification remains pending.

This is a technical starting repository, not a completed photon-spin study.

## Actual runs

- Built the modern photon-interface executable against LCG108 EL9/gcc13.
- Generated 1,000 new elastic SM gamma gamma -> tau tau events with an isolated
  MG5 3.5.2/GAMMA-UPC copy, seed 17017. Generator reports
  **0.2064 +/- 0.001645 pb** for the specified hard cuts. This is a small smoke
  sample, not a precision cross-section determination.
- Built and ran the legacy DY control with LCG105 EL9/gcc11, Pythia 8.310,
  Tauola 1.1.8/TauSpinner as supplied by that view, seed 37017.
- DY: 1,000 events, forced pi nu on both taus, mean spin weight
  **0.9918710566 +/- 0.0134664344**, consistent with unity (pull -0.604).
- HepMC2 read-back: 1,000 matching IDs; both weights preserved; two stable charged
  pions, two tau neutrinos, no stable taus per event.
- Repeated DY seed 37017: identical weights.csv and events.hepmc bytes.
- Six unit tests exercise valid input, duplicate IDs, missing events,
  nonfinite weights, photon-fraction-limit failure and hash-checked table staging.

Output locations (relative to repository):

```
outputs/elastic_generation/events.lhe
outputs/elastic_generation/manifest.json
outputs/elastic_generation/generation.log
outputs/dy_control/events.hepmc
outputs/dy_control/weights.csv
outputs/dy_control/run.json
outputs/dy_control/plots/
outputs/dy_control_repeat/
```

## Failed probes retained, not hidden

The first modern run could not find lhapdf.conf; env.sh now includes the stack's
share/LHAPDF directory as well as PDF data. The next run reached TauSpinner but
the library stopped with `electroweak tables not initialized. We stop run`.
The three official EW tables are absent from the inspected CVMFS install and
local workspace. Downloads failed because the current terminal cannot resolve
tauolapp.web.cern.ch. Failed directories are retained under outputs/dy_smoke*.
The modern driver now checks this dependency **before creating output**.

Do not bypass the library's initialization flag or substitute invented tables.
An installer accepts a supplied official, SHA-256-pinned archive. Table loading
and the modern photon run remain untested until that dependency is available.

## Physics qualification gates still required

- [ ] Supply official matching EW tables; record table and source hashes.
- [ ] Run the real photon interface; test 1e6 versus 1e9 photon fractions and
  verify the residual quark contribution is negligible across accepted phase space.
- [ ] Verify release-specific Born versus SM anomalous-moment convention.
  The installed ten-argument initialize_GSW differs from the newer paper API.
- [ ] Align tau masses, PDF and electroweak conventions between generation,
  Tauola and TauSpinner; record explicit values, not only library defaults.
- [ ] Compare gamma gamma spin-density elements against independent fixed-point
  QED calculations, including threshold and forward-angle tests.
- [ ] Validate photon spin-weight mean, positivity, angular dependence and
  same-seed reproducibility. DY success alone does not qualify photons.
- [ ] Compare DY weighted decay observables against a polarized reference with
  matched settings. The present unit-mean check is necessary but insufficient.
- [ ] Verify production/decay normalization and multiply physical branching
  fractions before quoting any absolute pi nu channel rates.
- [ ] Extend to rho/leptonic decays only with dedicated channel tests.
- [ ] Run a small Delphes sample and validate event-ID/weight joining, filters,
  detector migration and covariance-aware comparisons.

No existing parent-workspace production outputs were used as generated events
or modified. No remote repository was created and no CMS contact was made.

## EW-table follow-up

See [ew_tables.md](ew_tables.md) for the official-source search, acquisition
failure record and recovery procedure. Ten unit tests now cover acquisition
failure, complete versus mixed table groups, unsafe paths and the earlier
validation checks. The modern table probe builds, but loading and photon runs
remain blocked by the missing official data. No missing-table guard was removed.
