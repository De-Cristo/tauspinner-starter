import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('validate',Path(__file__).parents[1]/'scripts/validate.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run=Path(self.temp.name)
        (self.run/'run.json').write_text(json.dumps({
            'events':2,'spin_weight_mean':1.,'spin_weight_mean_error':.1,
            'photon_fraction_limit_max_difference':0.}))
        (self.run/'weights.csv').write_text('event_id,base_weight,spin_weight\n0,1,0.8\n1,1,1.2\n')
        (self.run/'events.hepmc').write_text('E 0 test\nE 1 test\n')

    def test_valid(self):
        self.assertEqual(module.inspect(self.run)['event_integrity'],'pass')

    def test_missing_events(self):
        (self.run/'events.hepmc').write_text('E 0 test\n')
        with self.assertRaises(ValueError): module.inspect(self.run)

    def test_duplicate_ids(self):
        (self.run/'weights.csv').write_text('event_id,base_weight,spin_weight\n0,1,.8\n0,1,1.2\n')
        with self.assertRaises(ValueError): module.inspect(self.run)

    def test_nonfinite(self):
        (self.run/'weights.csv').write_text('event_id,base_weight,spin_weight\n0,1,nan\n1,1,1.2\n')
        with self.assertRaises(ValueError): module.inspect(self.run)

    def test_limit_failure(self):
        meta=json.loads((self.run/'run.json').read_text())
        meta['photon_fraction_limit_max_difference']=.02
        (self.run/'run.json').write_text(json.dumps(meta))
        self.assertEqual(module.inspect(self.run)['photon_limit_check'],'fail')


if __name__=='__main__': unittest.main()
