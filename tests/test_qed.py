import importlib.util
from pathlib import Path
import unittest
import numpy as np

spec = importlib.util.spec_from_file_location('qed', Path(__file__).resolve().parents[1]/'scripts/check_qed.py')
qed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qed)


class QEDTests(unittest.TestCase):
    def test_clifford_algebra(self):
        for i in range(4):
            for j in range(4):
                expected = 2*qed.I*(1 if i == 0 else -1) if i == j else np.zeros((4,4))
                np.testing.assert_allclose(qed.G[i]@qed.G[j]+qed.G[j]@qed.G[i], expected)

    def test_massless_limit(self):
        alpha=1/137.
        for cosine in [0.,.5,.9]:
            expected=4*(4*np.pi*alpha)**2*(1+cosine**2)/(1-cosine**2)
            self.assertAlmostEqual(qed.kernel(50.,cosine,0.,alpha)/expected,1.,places=12)

    def test_ward_and_beam_symmetry(self):
        for energy in [2.,5.,50.]:
            for cosine in [0.,.6,.99]:
                value=qed.kernel(energy,cosine,1.77686,1/137.)
                self.assertGreater(value,0.)
                self.assertAlmostEqual(value,qed.kernel(energy,-cosine,1.77686,1/137.),places=10)
                self.assertLess(abs(qed.kernel(energy,cosine,1.77686,1/137.,True))/value,1e-10)
