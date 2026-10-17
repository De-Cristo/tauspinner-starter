#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def inspect(run):
    metadata = json.loads((run/'run.json').read_text())
    with (run/'weights.csv').open() as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != metadata['events']:
        raise ValueError('CSV event count mismatch')
    for i, row in enumerate(rows):
        if int(row['event_id']) != i:
            raise ValueError('Duplicate/missing event ID')
        if not all(math.isfinite(float(v)) for v in row.values()):
            raise ValueError('Nonfinite value')
        if not 0 <= float(row['spin_weight']) <= 4.00001:
            raise ValueError('Invalid spin weight')
    events = [line.split() for line in (run/'events.hepmc').read_text().splitlines() if line.startswith('E ')]
    if len(events) != len(rows):
        raise ValueError('HepMC count mismatch')
    for i, event in enumerate(events):
        if int(event[1]) != i:
            raise ValueError('HepMC ID mismatch')
    delta = metadata['photon_fraction_limit_max_difference']
    mean, err = metadata['spin_weight_mean'], metadata['spin_weight_mean_error']
    result = {
        'event_integrity': 'pass', 'events': len(rows),
        'unit_mean_pull': (mean-1)/err if err else None,
        'unit_mean_check': 'pass' if err and abs(mean-1) < 5*err else 'fail',
        'photon_limit_check': ('not_applicable' if metadata.get('channel') == 'dy'
                               else 'pass' if delta < 1e-4 else 'fail'),
        'physics_qualified': False,
        'hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [run/'run.json',run/'weights.csv',run/'events.hepmc']},
    }
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    result = inspect(args.run)
    target = args.output or args.run/'validation.json'
    with target.open('x') as handle:
        json.dump(result,handle,indent=2)
    print(json.dumps(result,indent=2))
    if result['unit_mean_check'] != 'pass' or result['photon_limit_check'] == 'fail':
        raise SystemExit(1)
