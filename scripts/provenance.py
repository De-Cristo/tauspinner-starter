#!/usr/bin/env python3
"""Record local source/build/dependency provenance without publishing anything."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''): h.update(block)
    return h.hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--binary',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    binary=args.binary.resolve()
    ldd=subprocess.check_output(['ldd',str(binary)],text=True)
    libs={}
    for line in ldd.splitlines():
        if 'not found' in line: raise RuntimeError('Unresolved shared library')
        for word in line.split():
            if word.startswith('/') and Path(word).is_file():
                p=Path(word).resolve()
                libs[str(p)]=digest(p)
    sources={}
    for folder in ['src','scripts','tests','patches']:
        for p in sorted((root/folder).glob('*')):
            if p.is_file(): sources[str(p.relative_to(root))]=digest(p)
    stack=Path(os.environ['TAUSPIN_STACK'])
    tauola=Path(os.environ.get('TAUOLA_ROOT',str(stack)))
    headers={str(p):digest(p) for p in [
        tauola/'include/TauSpinner/tau_reweight_lib.h',
        tauola/'include/TauSpinner/Particle.h',
        tauola/'include/Tauola/Version.h',
    ]}
    tables={}
    if os.environ.get('TAUSPIN_EW_TABLES'):
        for name in ['table.mu','table.down','table.up','provenance.json']:
            p=Path(os.environ['TAUSPIN_EW_TABLES'])/name
            tables[str(p)]=digest(p)
    record={'schema_version':1,'stack':str(stack),'binary':str(binary),
            'binary_sha256':digest(binary),'source_hashes':sources,
            'headers':headers,'library_hashes':libs,'ldd':ldd,
            'tauola_root':str(tauola),'table_hashes':tables,
            'compiler':subprocess.check_output(['c++','--version'],text=True),
            'physics_qualified':False}
    with args.output.open('x') as out: json.dump(record,out,indent=2)


if __name__=='__main__': main()
