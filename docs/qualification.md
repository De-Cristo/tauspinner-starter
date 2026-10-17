# What is validated, and what is not?

This page is the current checklist. Historical investigations in `validation.md`
and `ew_tables.md` are retained as provenance, not instructions to bypass checks.

## Ready for student exploration

- Official tables installed unchanged; hashes recorded.
- Isolated coordinate-limit patch documented and regression-tested.
- 1,000 photon events: finite weights, decay content, conservation and read-back.
- Same-seed photon CSV/HepMC reproducibility.
- DY control regression.
- 1,000-event Delphes technical handoff with explicit ID-based weight joining.
- Independent unpolarized QED Dirac-trace comparison: 30 energy/angle points
  spanning threshold to 500 GeV pair mass, maximum relative residual 7.05e-15.
  Photon Ward-identity and massless-limit checks are included.

## Before a public physics result

- [ ] Independently validate every relevant photon spin-density component and
  its mapping into the tau decay axes, not just the unpolarized production rate.
- [ ] Compare weighted decay observables with an independently polarized reference.
- [ ] Freeze and align actual tau masses, EW constants and decay inputs across
  MG5, Pythia, Tauola and TauSpinner. The official table headers differ and the
  current GSW initialization is explicit but not fully matched to them.
- [ ] Validate absolute LHE/Pythia normalization and branching fractions.
- [ ] Quantify uncertainties using same-event covariance, not independent errors
  for the weighted and unweighted histograms.
- [ ] Validate detector efficiencies, event filtering and detector-card assumptions
  for the proposed observable. A successful file conversion is insufficient.
- [ ] Validate additional tau decay modes before enabling them.

The QED kernel check (`scripts/check_qed.py`) computes the t/u-channel Dirac
trace independently and compares the unpolarized Born result with the actual
compiled TauSpinner kernel. It also tests a photon Ward identity. Its explicit
test mass is not a claim that all generator mass defaults have been aligned.
It does not validate the whole spin-weight calculation.

Run the kernel check in a new output file:

```bash
source env-photon.sh
python scripts/check_qed.py outputs/my_qed_check.json
python -m unittest discover -s tests -v
```

The successful record is `outputs/qed_kernel_check_v2.json`. The initial failed
probe is retained as `outputs/qed_kernel_check.json`: the Python adapter wrote
the wrong dynamically interposed Fortran common block and omitted the factor
four converting the fixed-spin coefficient into a final-spin sum. The corrected
adapter uses the global common block and explicit spin-projector normalization;
neither the upstream physics kernel nor the acceptance tolerance was changed.

The detector test uses Delphes 3.5.1pre12 and its shipped CMS example card.
See `outputs/detector_student_smoke/validation.json` for hashes and settings.
No official detector precision or analysis efficiency is claimed.

Until the unchecked items are resolved, keep `physics_qualified: false`.
