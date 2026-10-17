#!/usr/bin/env python3
"""Run a local detector smoke test and join CSV weights by checked event ID."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path, help='Completed photon smoke directory')
    parser.add_argument('output', type=Path, help='New detector output directory')
    parser.add_argument('--seed', type=int, default=48173)
    args = parser.parse_args()
    if args.seed <= 0:
        parser.error('Use a positive deterministic seed')
    binary = shutil.which('DelphesHepMC2')
    if not binary:
        parser.error('Delphes not found; source env-photon.sh first')
    binary = Path(binary).resolve()
    card = binary.parent.parent / 'cards/delphes_card_CMS.tcl'
    if not card.is_file():
        parser.error('Pinned CMS example card not found')
    with (args.run / 'weights.csv').open() as f:
        rows = list(csv.DictReader(f))
    by_id = {int(r['event_id']): r for r in rows}
    if not rows or len(by_id) != len(rows):
        raise ValueError('Empty input or duplicate event IDs')
    args.output.mkdir(parents=True, exist_ok=False)
    local_card = args.output / 'detector.tcl'
    local_card.write_text(f'set RandomSeed {args.seed}\n' + card.read_text())
    output = args.output / 'detector.root'
    command = [str(binary), str(local_card.resolve()), str(output.resolve()),
               str((args.run / 'events.hepmc').resolve())]
    with (args.output / 'delphes.log').open('x') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    import ROOT
    if ROOT.gSystem.Load(str(binary.parent.parent / 'lib/libDelphes.so')) < 0:
        raise RuntimeError('Cannot load Delphes ROOT dictionaries')
    file = ROOT.TFile.Open(str(output))
    tree = file.Get('Delphes')
    if not tree or tree.GetEntries() != len(rows):
        raise ValueError('Detector event count mismatch')
    seen = set()
    joined = []
    for event in tree:
        event_id = int(event.Event.At(0).Number)
        if event_id not in by_id or event_id in seen:
            raise ValueError('Missing/duplicate/unexpected detector event ID')
        seen.add(event_id)
        row = by_id[event_id]
        stable = [p for p in event.Particle if p.Status == 1]
        if sum(abs(p.PID) == 211 for p in stable) != 2 or sum(abs(p.PID) == 16 for p in stable) != 2:
            raise ValueError('Truth daughters did not survive detector input')
        joined.append({'event_id': event_id, 'base_weight': float(row['base_weight']),
                       'spin_sm_weight': float(row['base_weight']) * float(row['spin_weight']),
                       'n_tracks': len(event.Track), 'n_jets': len(event.Jet),
                       'missing_et_GeV': float(event.MissingET.At(0).MET)})
    with (args.output / 'joined_weights.csv').open('x') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(joined[0]))
        writer.writeheader()
        writer.writerows(joined)
    report = {'schema_version': 1, 'status': 'technical_pass',
              'events': len(seen), 'seed': args.seed,
              'weight_join': 'explicit_event_id_not_row_offset',
              'named_weight_preservation_in_ROOT': 'not_assumed_use_joined_csv',
              'physics_qualified': False, 'detector_card': str(card),
              'command': command, 'hashes': {str(p): digest(p) for p in
                  [binary, card, local_card, args.run/'events.hepmc',
                   args.run/'weights.csv', output, args.output/'joined_weights.csv']}}
    (args.output / 'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
