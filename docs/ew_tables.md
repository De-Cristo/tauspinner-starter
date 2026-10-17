# Official EW tables: investigation and recovery

## Superseding resolution (2026-10-17)

The supplied official archive contains all three tables. Loading and the
1,000-event photon test now pass with an isolated collinear-coordinate source
fix. See [table_resolution.md](table_resolution.md) for hashes, caveats and
the tested runtime. The investigation below is the historical blocked state;
its direct unpatched photon command is not the current supported workflow.
Use `scripts/smoke_photon.sh` instead.

## Outcome (2026-10-16)

**Unresolved data acquisition; no photon physics result is claimed.**

The official photon example explicitly initializes `table.mu`, `table.down`, and
`table.up` with `initTables`. The current executable's missing-table check remains
enabled. No library initialization flags were bypassed and no numerical table
was constructed by hand.

The matching source is TAUOLA **1.1.9 / TauSpinner 2.1.2**, corresponding to the
LCG108 `1.1.9.atlas1-3301e` installation. Do not silently replace it with 1.1.10:
the GSW API differs, and release-specific initialization must be requalified.

## Confirmed sources

1. [Official release index](https://tauolapp.web.cern.ch/tauolapp/): identifies the
   1.1.9 release and its matching distribution. Its online Doxygen documentation
   describes development code, not necessarily this release.
2. [Official 1.1.9 archive](https://tauolapp.web.cern.ch/tauolapp/resources/TAUOLA.1.1.9/TAUOLA.1.1.9-LHC.tar.gz).
3. [CERN LCG source mirror](https://lcgpackages.web.cern.ch/tarFiles/sources/MCGeneratorsTarFiles/TAUOLA.1.1.9-LHC.tar.gz).
   This exact URL is recorded in the installed package's
   `logs/download-tauola++-1.1.9.atlas1.cmake`, not guessed from a third-party mirror.
4. [Photon algorithm, Appendix A](https://arxiv.org/abs/2506.15213): loads the three
   tables and configures both the quark and photon contributions. It does not
   establish a table-free initialization for our installed release.
5. [Electroweak implementation, Appendices B/C/E](https://arxiv.org/abs/2012.10997):
   describes DIZET/KKMC-generated tables and the TauSpinner-specific table format.
   In particular, Appendix E discusses a modified `BornV.h` format. Arbitrary
   KKMC tables are therefore **not** automatically suitable replacements.

The tables contain electroweak form factors for the shared neutral-current
machinery, not an elastic proton flux or detector response. Their presence does
not imply that the photon hard process is evaluated at NLO.

## Searches and failed acquisition

- Installed modern Tauola packages have libraries, headers and build logs, but
  no matching table triple in the inspected package.
- CERN's accessible `lcg/sources/LCG_88` Tauola cache contains older releases
  (through 1.1.6 variants), not the matching photon release.
- The earlier workspace search found no matching table files or source archive.
- HTTP downloads of both the official release and CERN mirror failed with DNS
  errors. See `deps/official_1p1p9_attempt_20261016/acquisition.json`.
- Web search could read the papers and release index but could not deliver the
  binary archive to this filesystem. The configured remote-workspace service
  was also unavailable. No credentials or private data were sent to an archive host.
- Release source inspection and photon execution with the correct data are still
  pending. We have **not** proved that the release archive contains precomputed
  tables; the acquisition tool inventories it rather than assuming that it does.

## Recovery procedure

Run from a network-enabled environment, or supply the archive locally:

```bash
cd tau-spin-study
python3 scripts/fetch_official_tauola.py --output deps/official_1p1p9_download
```

The script uses only the two above HTTPS sources, records failures, computes an
archive hash and inventories complete table triples in a single directory. A
computed checksum is a reproducibility identifier, **not** a publisher signature.
If an independently known digest exists, pass `--sha256 DIGEST`.

Then review `acquisition.json`. If a complete matching triple is included:

```bash
python3 scripts/stage_tables.py deps/official_1p1p9_download/TAUOLA.1.1.9-LHC.tar.gz \
  --sha256 RECORDED_ARCHIVE_SHA256 \
  --table-prefix EXACT_COMPLETE_GROUP_FROM_INVENTORY \
  --output deps/ew_tables_1p1p9
source env.sh
cmake -S . -B build
cmake --build build -j2
./build/check-tables deps/ew_tables_1p1p9
export TAUSPIN_EW_TABLES="$PWD/deps/ew_tables_1p1p9"
./build/tau-spin gg outputs/elastic_generation/events.lhe outputs/elastic_spin_tables 1000 27017
./build/readcheck outputs/elastic_spin_tables/events.hepmc outputs/elastic_spin_tables/weights.csv
python scripts/validate.py outputs/elastic_spin_tables
```

The probe must load all three files and print finite EW header parameters.
Its current status is **compiled, not tested with actual table data**. Table
headers and initialization conventions must be reviewed before interpreting
any resulting weights physically. The table installer refuses to mix files
from different directories or silently choose among multiple schemes.

If the archive contains no complete triple, inspect its supplied examples and
DIZET instructions (the inventory lists relevant source members). Obtain the
corresponding official table distribution or reproduce them with the authors'
documented DIZET generator and inputs. Do not invent a generic `make` command,
reuse an arbitrary KKMC table, or create identity/zero-filled tables.

Even after acquisition, verify the installed release's Born/anomalous-moment
convention, the photon-to-quark limit test, event weights, spin normalization,
reproducibility and fixed-point photon amplitudes. Unit-mean or parser success
alone is not physics qualification.
