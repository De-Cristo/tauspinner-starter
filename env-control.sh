#!/usr/bin/env bash
# Legacy, supported DY control. Never use this stack for photon spin weights.
source /cvmfs/sft.cern.ch/lcg/views/LCG_105/x86_64-el9-gcc11-opt/setup.sh
export TAUSPIN_STACK=/cvmfs/sft.cern.ch/lcg/views/LCG_105/x86_64-el9-gcc11-opt
export LHAPDF_DATA_PATH=/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current:${TAUSPIN_STACK}/share/LHAPDF
