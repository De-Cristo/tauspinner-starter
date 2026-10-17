#!/usr/bin/env python3
"""Independent Dirac-trace check of the unpolarized Born photon kernel."""
import argparse
import ctypes as ct
import hashlib
import json
import math
import os
from pathlib import Path
import numpy as np

I = np.eye(4, dtype=complex)
Z = np.zeros((2, 2), dtype=complex)
pauli = [np.array([[0,1],[1,0]]), np.array([[0,-1j],[1j,0]]), np.diag([1,-1])]
G = [np.diag([1,1,-1,-1])] + [np.block([[Z,s],[-s,Z]]) for s in pauli]


def slash(p):
    return p[0]*G[0] - sum(p[i]*G[i] for i in range(1,4))


def norm(p):
    return p[0]**2 - np.dot(p[1:],p[1:])


def kernel(energy, cosine, mass, alpha, ward=False):
    momentum = math.sqrt(energy**2-mass**2)
    p = np.array([energy, momentum*math.sqrt(1-cosine**2),0,momentum*cosine])
    pp = np.array([energy,*(-p[1:])])
    k1 = np.array([energy,0,0,energy])
    k2 = np.array([energy,0,0,-energy])
    polarizations = [np.array([0,1,0,0]),np.array([0,0,1,0])]
    total = 0.
    for e1 in ([k1/energy] if ward else polarizations):
        for e2 in polarizations:
            a = (slash(e1)@(slash(p-k1)+mass*I)@slash(e2)/(norm(p-k1)-mass**2)
                 + slash(e2)@(slash(p-k2)+mass*I)@slash(e1)/(norm(p-k2)-mass**2))
            total += np.trace((slash(p)+mass*I)@a@(slash(pp)-mass*I)@G[0]@a.conj().T@G[0]).real
    return total*(4*math.pi*alpha)**2/4


class Beam(ct.Structure):
    _fields_ = [('energy',ct.c_double),('mass_in',ct.c_double),
                ('mass_out',ct.c_double),('id_in',ct.c_int),('id_out',ct.c_int)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    path=Path(os.environ['TAUOLA_ROOT'])/'lib/libTauolaTauSpinner.so'
    for dependency in ['libLHAPDF.so','libTauolaFortran.so','libTauolaCxxInterface.so']:
        ct.CDLL(dependency, mode=ct.RTLD_GLOBAL | os.RTLD_LAZY)
    lib=ct.CDLL(str(path))
    # The Fortran common block is interposed by the globally loaded dependency.
    beam=Beam.in_dll(ct.CDLL(None),'t_beampm_')
    # Explicit test inputs, not an assertion of aligned generator defaults.
    mass=1.77686
    alpha=7.2973525693e-3
    beam.mass_out=mass
    rows=[]
    for energy in [mass*1.01,2.,5.,25.,50.,250.]:
        for cosine in [-.99,-.6,0.,.6,.99]:
            iqed=ct.c_int(0)
            e,theta,a,b=map(ct.c_double,[energy,math.acos(cosine),0.,0.])
            r=(ct.c_double*16)()
            lib.dipolgammarij_(ct.byref(iqed),ct.byref(e),ct.byref(theta),ct.byref(a),ct.byref(b),r)
            # R_tt has final spin-projector factors 1/2 for each tau. Sum both
            # final spins (factor 4), then undo Fnorm=4*pi^2*alpha^2.
            upstream=4*r[15]*4*math.pi**2*alpha**2
            direct=kernel(energy,cosine,mass,alpha)
            relative=abs(direct-upstream)/abs(direct)
            ward=abs(kernel(energy,cosine,mass,alpha,True))/abs(direct)
            rows.append(dict(energy_GeV=energy,cos_theta=cosine,direct=direct,
                             upstream=upstream,relative_difference=relative,ward_residual=ward))
    passed=all(r['relative_difference']<1e-8 and r['ward_residual']<1e-10 for r in rows)
    report={'scope':'unpolarized_Born_kernel_not_full_spin_density_validation',
            'mass_GeV':mass,'alpha':alpha,'iqed':0,'points':rows,
            'gate':'pass' if passed else 'fail','physics_qualified':False,
            'library_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with args.output.open('x') as f: json.dump(report,f,indent=2)
    print(report['gate'], 'max relative difference',max(r['relative_difference'] for r in rows))
    if not passed: raise SystemExit(1)


if __name__=='__main__': main()
