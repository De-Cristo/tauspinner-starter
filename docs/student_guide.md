# Your first tau-spin study

## What question are we asking?

Two photons can produce a tau-minus and a tau-plus. Each tau decays before we
can detect it. The directions and energies of its decay products carry information
about its spin. Our first question is:

**Do the pion distributions change when we include the correlation between the
two tau spins? Does that change survive a simplified detector simulation?**

You do not need to write a generator to start. This repository already provides
a small working example. It is a learning project, not yet a validated public
prediction or an official CMS simulation.

## What each program does

| Program | Job | Output |
|---|---|---|
| MadGraph + GAMMA-UPC | Generate the photons and stable tau pair | `events.lhe` |
| Pythia | Decay each tau without polarization | Daughter four-momenta |
| TauSpinner | Calculate a number describing the spin correlation | `spin_weight` |
| HepMC | Store generated particles and their history | `events.hepmc` |
| Delphes | Simulate an approximate detector response | `detector.root` |
| Our Python scripts | Check and compare the results | Tables and plots |

TauSpinner does not generate a second event. It gives an existing event a weight.
For our deliberately unpolarized starting sample:

\[
w_{\mathrm{correlated}}=w_{\mathrm{input}}w_{\mathrm{spin}}.
\]

Use the same event twice in two histograms: once with the input weight, once
with the correlated weight. Do not multiply twice. Do not use this recipe on an
already polarized sample without understanding the appropriate weight ratio.

## Step 1: look at the existing results

If you just cloned GitHub, these examples are not present yet. First follow
[installation](installation.md) to build dependencies and generate the inputs.

The following paths are relative to `tau-spin-study/`:

- `outputs/photon_smoke/plots/`: five truth-level plots.
- `outputs/photon_smoke/weights.csv`: one line per generated event.
- `outputs/photon_smoke/validation.json`: machine-readable checks.
- `outputs/detector_student_smoke/detector.root`: detector output.
- `outputs/detector_student_smoke/joined_weights.csv`: detector observables and
  spin weights joined using checked event IDs.

Start with `z_minus.png` and `z_plus.png`. Here
\(z_\pm=E_{\pi^\pm}/E_{\tau^\pm}\) uses energies in the laboratory frame.
The plot tells you how much of a tau's energy its charged pion carries.
Individual distributions need not show a large effect: a correlation can be
more visible in the **joint** distribution of the two pion energies.

`visible_mass.png` uses only the two pions, so it is not the true tau-pair mass:
neutrinos carry away energy. `m_tautau.png` is a truth-level consistency check.
`spin_weight.png` shows how strongly individual events are reweighted.

These are small samples. A fluctuation is not evidence for new physics.

## Step 2: run your own copy

Open a new terminal on this machine. Run commands from this directory:

```bash
cd /path/to/tauspinner-starter
bash scripts/smoke_photon.sh outputs/elastic_generation/events.lhe outputs/my_first_run 1000 27018
```

This uses the existing 1,000 hard events and makes a new set of tau decays. It
does **not** create independent photon-production kinematics. The last number
is a random seed: the same input and seed should reproduce the same result.
The output directory must be new. Keep old results instead of overwriting them.

The script builds the program, loads the tables, runs it, checks the output,
and draws plots. Success means the command exits without an error and
`outputs/my_first_run/validation.json` reports passing checks. It does not mean
every physics assumption has been validated.

These commands require CERN CVMFS and the locally prepared dependencies.
On another computer, first ask a supervisor to help reproduce the pinned
environment and official-table installation described in the main README.

## Step 3: run the detector example

```bash
source env-photon.sh
python scripts/delphes_smoke.py outputs/my_first_run outputs/my_first_detector --seed 48174
```

This uses the installed CMS **example** detector card without pileup. It is not
an approved CMS campaign configuration. The output contains a ROOT file, log,
copied detector card, validation report and `joined_weights.csv`.

The script checks that every generated event has exactly one matching detector
event. Do not assume ROOT kept both named HepMC weights: use the checked CSV
join. Never join by row number after filtering or sorting. ROOT files may differ
in timestamps even when physics output is reproducible.

The event record describes the central photon collision. It does not simulate
outgoing proton tagging, proton remnants, photon transverse momentum or pileup.

## Step 4: use a control sample

In a separate terminal:

```bash
cd /path/to/tauspinner-starter
bash scripts/smoke_control.sh outputs/my_control 1000 37018
```

This produces a Z/virtual-photon tau-pair control. It tests a familiar channel,
but uses a different installed TauSpinner version. Passing this control does
not prove the photon calculation is correct.

## A manageable first project

1. Explain the existing five truth plots in your own words.
2. Make a two-dimensional plot of `z_minus` versus `z_plus` with each weight.
3. Compare reconstructed track counts and missing transverse momentum using
   the detector CSV. Explain why neutrinos produce missing momentum.
4. Repeat with another decay and detector seed. Separate fluctuations caused
   by decays from those caused by detector smearing.
5. Write a short note listing cuts, versions, seeds, weighting and limitations.
6. Discuss the qualification checklist with your supervisor before interpreting
   an effect size, extracting a coupling or quoting expected event counts.

Use a paired bootstrap (resample event IDs and retain both weights together)
for uncertainty on differences or ratios. The two histograms share events and
are not statistically independent. Existing plot errors are simple sumw2 errors,
not a complete uncertainty on their difference.

## Why we do not quote event yields yet

Both taus are forced to decay to a charged pion and a neutrino. Nature also
allows other decay modes. Our histograms are conditional on this chosen mode.
For an absolute selected yield the general relation would be

\[
N=\mathcal L\,\sigma(pp\to p\tau^+\tau^-p)
\,\mathrm{BR}(\tau\to\pi\nu)^2\,\epsilon.
\]

Here luminosity \(\mathcal L\), cross section \(\sigma\), branching fraction
BR and selection efficiency \(\epsilon\) must use consistent units and
validated inputs. Do not treat the CSV generator weights as cross sections in pb.
No branching fraction is silently inserted by this repository.

## Common problems

| Message or symptom | What to do |
|---|---|
| Output exists | Choose a new directory; do not delete a previous result blindly |
| Missing table/library | Source `env-photon.sh`; check the setup with your supervisor |
| Not enough LHE events | Request at most the available count; do not repeat events to inflate statistics |
| Validation fails | Keep the logs and stop; do not bypass the check |
| No visible spin effect | Study joint observables and statistical uncertainty first |
| Font-cache warning | Usually harmless if plots exist; choose a writable cache directory if needed |

## Small glossary

- **Truth:** generated particle information before detector simulation.
- **Four-vector:** energy and three momentum components of a particle.
- **Spin correlation:** how the two particles' spins are related.
- **Weight:** a numerical contribution of an event to a histogram.
- **Seed:** integer controlling a reproducible pseudorandom sequence.
- **Smoke test:** a short test that checks whether the software chain works.
- **Physics validation:** comparison against independently established physics.
- **Branching fraction:** probability of a particular decay channel.
- **ESS:** effective sample size; uneven weights contain less information than
  equally weighted events. It is not automatically the uncertainty of a ratio.
