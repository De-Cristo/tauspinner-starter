#!/usr/bin/env python3
"""Install official EW tables from a user-supplied, hash-pinned source archive."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('archive',type=Path)
    parser.add_argument('--sha256',required=True)
    parser.add_argument('--output',type=Path,default=Path('deps/ew_tables'))
    parser.add_argument('--table-prefix', help='Exact archive directory containing one complete matched triple')
    args = parser.parse_args()
    digest = hashlib.sha256(args.archive.read_bytes()).hexdigest()
    if digest != args.sha256:
        raise ValueError('Archive checksum mismatch')
    data = {}
    with tarfile.open(args.archive) as archive:
        groups = {}
        for member in archive.getmembers():
            name = Path(member.name).name
            if member.isfile() and name in {'table.mu','table.down','table.up'}:
                group = groups.setdefault(str(Path(member.name).parent), {})
                if name in group:
                    raise ValueError('Duplicate table member')
                group[name] = member
        complete = {prefix: members for prefix, members in groups.items()
                    if len(members) == 3}
        if args.table_prefix:
            if args.table_prefix not in complete:
                raise ValueError('Requested prefix does not contain a complete table triple')
            selected = args.table_prefix
        elif len(complete) == 1:
            selected = next(iter(complete))
        else:
            raise ValueError('Need exactly one complete table triple, or --table-prefix. Available: '
                             + ', '.join(sorted(complete)))
        for name in ['table.mu','table.down','table.up']:
            member = complete[selected][name]
            if member.size > 200*1024*1024:
                raise ValueError('Oversized table')
            content = archive.extractfile(member).read()
            if not content.strip():
                raise ValueError('Empty table')
            data[name]=content
    args.output.mkdir(parents=True,exist_ok=False)
    hashes={}
    for name,content in data.items():
        (args.output/name).write_bytes(content)
        hashes[name]=hashlib.sha256(content).hexdigest()
    (args.output/'provenance.json').write_text(json.dumps({
        'archive':str(args.archive.resolve()),'archive_sha256':digest,'tables':hashes,
        'archive_table_prefix':selected,
        'checksum_authentication':'caller_supplied_hash_not_necessarily_publisher_authenticated',
        'physics_qualified':False,
    },indent=2)+'\n')


if __name__=='__main__':
    main()
