#!/usr/bin/env python3
"""Shape-only truth plots; never interprets Pythia's event weight as pb."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    with (args.run / 'weights.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    arrays = {key: np.array([float(r[key]) for r in rows]) for key in rows[0]}
    if not all(np.isfinite(a).all() for a in arrays.values()):
        raise ValueError('Nonfinite data')
    out = args.run / 'plots'
    out.mkdir(exist_ok=False)
    weights = arrays['base_weight'] * arrays['spin_weight']
    base = arrays['base_weight']
    for key, label, bins in [
        ('z_minus', r'$E_{\pi^-}/E_{\tau^-}$ (lab)', np.linspace(0,1,31)),
        ('z_plus', r'$E_{\pi^+}/E_{\tau^+}$ (lab)', np.linspace(0,1,31)),
        ('visible_mass', r'$m_{\pi\pi}$ [GeV]', 35),
        ('m_tautau', r'$m_{\tau\tau}$ [GeV]', 35),
    ]:
        edges = np.histogram_bin_edges(arrays[key], bins=bins)
        fig, ax = plt.subplots(figsize=(7,5))
        for w, name in [(base,'Unpolarized input'),(weights,'TauSpinner SM spin')]:
            values = np.histogram(arrays[key],edges,weights=w)[0] / np.sum(w)
            errors = np.sqrt(np.histogram(arrays[key],edges,weights=w*w)[0]) / abs(np.sum(w))
            ax.stairs(values,edges,label=name)
            ax.errorbar((edges[1:]+edges[:-1])/2,values,yerr=errors,fmt='none',alpha=.45)
        ax.set(xlabel=label,ylabel='Fraction / bin',title='Technical validation: forced pi nu decays')
        ax.legend(); fig.tight_layout(); fig.savefig(out / (key+'.png'),dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(6,5))
    ax.hist(arrays['spin_weight'],bins=40,histtype='step')
    ax.set(xlabel='TauSpinner spin weight',ylabel='Events',title='Technical validation, not physics-qualified')
    fig.tight_layout(); fig.savefig(out/'spin_weight.png',dpi=160); plt.close(fig)
    (out/'summary.json').write_text(json.dumps({
        'events': len(rows), 'sum_base_weights': float(base.sum()),
        'sum_spin_weights': float(weights.sum()),
        'spin_weight_ess': float(weights.sum()**2 / (weights@weights)),
        'normalization': 'separately normalized shapes; forced-decay branching fractions NOT included',
        'errors': 'sumw2; shared-event covariance and normalization uncertainty not shown',
    },indent=2)+'\n')


if __name__ == '__main__':
    main()
