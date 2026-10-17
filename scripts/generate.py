#!/usr/bin/env python3
"""Generate new SM elastic events in an isolated copy of a gamma-UPC MG5."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mg5', required=True, type=Path,
                    help='Configured MG5 installation, copied before use')
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--events', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=17017)
    args = ap.parse_args()
    if args.events < 1 or not 1 <= args.seed < 900000000:
        ap.error('Invalid event count or seed')
    source = args.mg5.resolve()
    if not (source / 'PLUGIN/gamma-UPC/ElasticPhotonPhotonFlux.f90').is_file():
        ap.error('A configured GAMMA-UPC installation is required; no generic photon PDF fallback')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    local = out / 'mg5'
    shutil.copytree(source, local, symlinks=True)
    process = out / 'process'
    card = out / 'generate.mg5'
    card.write_text(f'''set automatic_html_opening False
set run_mode 0
import model sm
generate a a > ta+ ta-
output {process}
launch {process}
0
set nevents {args.events}
set iseed {args.seed}
set ebeam1 6800
set ebeam2 6800
set lpp1 2
set lpp2 2
set pdlabel chff
set use_syst False
set ptl 10
set etal 2.5
set drll 0.4
set mmll 50
set param_card sminputs 1 137.035999084
done
quit
''')
    with (out / 'generation.log').open('w') as log:
        subprocess.run([str(local / 'bin/mg5_aMC'), str(card)], cwd=out,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    events = process / 'Events/run_01/unweighted_events.lhe.gz'
    raw = out / 'events.lhe'
    with gzip.open(events, 'rb') as src, raw.open('wb') as dst:
        shutil.copyfileobj(src, dst)
    observed = sum(line.strip() == '<event>' for line in raw.open())
    if observed != args.events:
        raise RuntimeError(f'Wrong count: {observed} != {args.events}')
    inputs = [card, process / 'Cards/run_card.dat', process / 'Cards/param_card.dat',
              source / 'PLUGIN/gamma-UPC/ElasticPhotonPhotonFlux.f90', source / 'VERSION']
    (out / 'manifest.json').write_text(json.dumps({
        'process': 'elastic gamma gamma -> tau+ tau-', 'events': observed,
        'seed': args.seed, 'input_source': str(source),
        'shower': False, 'kt_smearing': False,
        'cuts': {'mll_min': 50, 'ptl_min': 10, 'abs_tau_rapidity_max': 2.5, 'drll_min': 0.4},
        'hashes': {str(p): sha(p) for p in inputs + [raw]},
    }, indent=2) + '\n')


if __name__ == '__main__':
    main()
