# Official-table resolution (2026-10-17)

## Provenance

The supplied official TAUOLA 1.1.9 archive was verified against SHA-256
`4eb69f38bc0163568034f95b47d1ae461becbff9935921d57e49d3583cb3c158`.
This identifies the HTTPS download; it is not a publisher-authenticated digest.
The three tables from `TAUOLA/TauSpinner/examples/Dizet-example` were staged
unchanged in `deps/ew_tables_1p1p9`. Individual hashes are in its `provenance.json`.
No EW tables or physical matrix elements were invented.

The actual table-loader categories are 0=mu, 1=down, 2=up, not PDG IDs.
All three load successfully. Their upstream headers are not identical:
mu MZ=91.187, GammaZ=2.4982765608, sin2thetaW=0.2235194639657;
quark MZ=91.1876, GammaZ=2.498111432484, sin2thetaW=0.2233275841914.
These differences remain explicit convention-qualification inputs.

## Additional runtime fixes

With tables present, exactly collinear events exposed a coordinate singularity
in upstream `Particle::getAnglePhi`: 0/0 for zero transverse momentum propagated
into EW table indexing. `patches/particle-collinear.patch` chooses zero rotation
for the undefined azimuth and zero-vector polar angle. It does not perturb
momenta, add photon kT, alter tables, or modify nondegenerate formulas.
`scripts/build_photon_tauola.sh` builds an isolated patched official source;
CVMFS is unchanged. `env-photon.sh` selects it. The C++ collinear regression
checks finite boosts, mass shells and inverse transformations.

Pythia's disabled parton level does not itself decay the process record. The
driver now explicitly constructs the central two-photon/two-tau hard system
and invokes the configured unpolarized pi-nu decays. Exported photon events
contain no artificial Z and no outgoing proton model. Read-back verifies
central four-momentum conservation, daughter content and named weights.

## Completed technical test

Output: `outputs/photon_smoke`, 1,000 events, decay seed 27017, using the existing
independent-repository elastic LHE. No MG5 events were regenerated in this step.

- Spin-weight mean: 1.0105855676916502 +/- 0.010380760150249895 (pull 1.020).
- Maximum weight difference for photon fractions 1e6 versus 1e9: 8.25877e-7.
- HepMC read-back, pi-nu content and named-weight validation pass.
- Same-seed CSV and HepMC are byte-identical to the repeated photon runs.
- Ten Python unit tests pass; compiled collinear and table-loading checks pass.
- Five truth-level shape plots are under `outputs/photon_smoke/plots`.
- `validation.json` records output hashes; `build_manifest.json` records sources,
  resolved libraries, table hashes and runtime provenance.

The source configures zero anomalous dipoles and its photon branch uses iqed=0.
This is a Born technical setup, not an NLO result. Plotting emitted font-cache
warnings; outputs were produced. No warning-free claim is made.

## Remaining qualification

`physics_qualified: false`. Independent photon spin-density/QED fixed-point
checks, input-convention alignment, polarized-reference comparisons, absolute
channel normalization and Delphes validation remain required. The unit-mean
and photon-fraction checks alone do not establish physical correctness.
Both tau decays are forced pi-nu; plots are conditional shapes, not inclusive
channel cross sections. Existing parent-workspace samples were not modified.
