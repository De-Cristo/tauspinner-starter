# Detector handoff

## Tested shortcut

The 1,000-event handoff now passes with the installed Delphes CMS example card.
For beginner instructions use [student_guide.md](student_guide.md). Run:

```bash
source env-photon.sh
python scripts/delphes_smoke.py outputs/photon_smoke outputs/my_detector
```

The script preserves the input, records hashes, checks event IDs and truth
daughter content, and writes `joined_weights.csv`. It does not assume that
named weights survive inside ROOT. The longer discussion below explains the
limitations; detector efficiencies and analysis selections are not yet qualified.

The tested photon output is `outputs/photon_smoke/events.hepmc`. Its beams are
the two hard photons, not a complete exclusive proton-proton event record.
No outgoing protons or forward-proton transport are included. Reader acceptance
of this central-system representation must be tested before detector studies.

The output `events.hepmc` is HepMC2 ASCII produced by HepMC3's official writer.
Use a Delphes installation with a HepMC2 reader:

```bash
DelphesHepMC2 /path/to/delphes_card_CMS.tcl detector.root outputs/elastic_spin/events.hepmc
```

This command is a downstream interface, not a claim of a validated detector run.
First read a tiny sample, check the exact event count and event numbering,
then inspect the reader's handling of multiple event weights. Do not assume all
named weights survive into ROOT. `weights.csv` is the authoritative fallback,
joined using the explicitly validated generator event ID, never an unchecked row
offset. Preserve the map when filtering events. Do not run TauSpinner again on
reconstructed objects: it needs truth tau parents and neutrinos.

The initial sample contains charged pions and neutrinos from forced pi nu decays.
No inclusive tau branching-fraction interpretation is allowed. Its elastic beam
record does not include a validated forward-proton transport model. Photon kT,
pileup, detector response and proton tagging are separate additions.

Useful first observables: charged-pion energy fractions, their 2D correlation,
visible pair mass and angular correlations. Compare the **same events** with
baseline and spin weights so detector migration is controlled. Later add rho nu
and validated decay-plane observables before claiming CP sensitivity.
