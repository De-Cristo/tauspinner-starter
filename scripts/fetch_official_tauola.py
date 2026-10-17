#!/usr/bin/env python3
"""Acquire the release matching our CVMFS library; never synthesize EW tables.

Checksums computed here establish reproducibility, NOT a publisher signature.
An optional externally known --sha256 makes this a pinned download.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import urllib.request

URLS = [
    'https://tauolapp.web.cern.ch/tauolapp/resources/TAUOLA.1.1.9/TAUOLA.1.1.9-LHC.tar.gz',
    'https://lcgpackages.web.cern.ch/tarFiles/sources/MCGeneratorsTarFiles/TAUOLA.1.1.9-LHC.tar.gz',
]
TABLES = {'table.mu', 'table.down', 'table.up'}
MAX_BYTES = 200 * 1024 * 1024


def inspect_archive(path):
    """Inventory full table triples together; do not mix schemes or directories."""
    groups = {}
    evidence = []
    with tarfile.open(path, 'r:gz') as archive:
        for member in archive.getmembers():
            p = PurePosixPath(member.name)
            if p.is_absolute() or '..' in p.parts:
                raise ValueError('Unsafe archive member path')
            if not member.isfile():
                continue
            if p.name in TABLES:
                if member.size > MAX_BYTES:
                    raise ValueError('Oversized table')
                data = archive.extractfile(member).read()
                if not data.strip():
                    raise ValueError('Empty table')
                key = str(p.parent)
                if p.name in groups.setdefault(key, {}):
                    raise ValueError('Duplicate table member')
                groups[key][p.name] = {'member': member.name, 'bytes': len(data),
                                     'sha256': hashlib.sha256(data).hexdigest()}
            if p.name in {'EWtables.cxx', 'EWtables.h', 'tau-reweight-test.cxx',
                          'table-parsing-test.cxx', 'BornV.h', 'initwksw.f'}:
                evidence.append(member.name)
    return {'complete_table_groups': {p: entries for p, entries in groups.items()
                                      if set(entries) == TABLES},
            'incomplete_table_groups': {p: entries for p, entries in groups.items()
                                        if set(entries) != TABLES},
            'source_evidence_members': evidence}


def fetch(output, expected=None, timeout=20):
    output.mkdir(parents=True, exist_ok=False)
    record = {'schema_version': 1, 'release': 'TAUOLA 1.1.9 / TauSpinner 2.1.2',
              'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'official_release_page': 'https://tauolapp.web.cern.ch/tauolapp/',
              'mirror_provenance': 'CERN LCG tauola++-1.1.9.atlas1 download recipe',
              'expected_sha256': expected, 'attempts': [], 'status': 'blocked',
              'physics_qualified': False}
    for index, url in enumerate(URLS):
        partial = output / f'download-{index}.part'
        attempt = {'url': url}
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                attempt['resolved_url'] = response.url
                if not response.url.startswith('https://'):
                    raise ValueError('Non-HTTPS redirect refused')
                size = 0
                with partial.open('xb') as stream:
                    while block := response.read(1024 * 1024):
                        size += len(block)
                        if size > MAX_BYTES:
                            raise ValueError('Download exceeds 200 MiB limit')
                        stream.write(block)
            digest = hashlib.sha256(partial.read_bytes()).hexdigest()
            if expected and digest != expected:
                raise ValueError('Publisher/user-pinned checksum mismatch')
            inventory = inspect_archive(partial)
            final = output / 'TAUOLA.1.1.9-LHC.tar.gz'
            partial.rename(final)
            attempt['status'] = 'downloaded'
            record.update(status='downloaded_not_physics_validated', archive=str(final),
                          archive_sha256=digest,
                          checksum_authentication='externally_pinned' if expected else
                          'computed_from_https_download_not_publisher_authenticated',
                          inventory=inventory)
        except Exception as exc:
            attempt.update(status='failed', error=f'{type(exc).__name__}: {exc}')
            if partial.exists():
                partial.unlink()
        record['attempts'].append(attempt)
        if attempt['status'] == 'downloaded':
            break
    (output / 'acquisition.json').write_text(json.dumps(record, indent=2) + '\n')
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New provenance directory')
    parser.add_argument('--sha256', help='Optional independently known archive hash')
    parser.add_argument('--timeout', type=int, default=20)
    args = parser.parse_args()
    if args.sha256 and (len(args.sha256) != 64 or any(c not in '0123456789abcdef' for c in args.sha256)):
        parser.error('--sha256 must be a lowercase SHA-256 digest')
    result = fetch(args.output, args.sha256, args.timeout)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['status'].startswith('downloaded') else 1)
