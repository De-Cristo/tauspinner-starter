import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location('fetch', Path(__file__).parents[1]/'scripts/fetch_official_tauola.py')
fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch)


class AcquisitionTests(unittest.TestCase):
    def archive(self, root, names):
        path = root/'source.tar.gz'
        with tarfile.open(path,'w:gz') as tar:
            for name in names:
                # Synthetic parser test data, never installed as physics tables.
                data=b'PARSER TEST ONLY\n'
                info=tarfile.TarInfo(name); info.size=len(data)
                tar.addfile(info, io.BytesIO(data))
        return path

    def test_same_directory_triple(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive=self.archive(Path(tmp), ['scheme/'+x for x in fetch.TABLES])
            inventory=fetch.inspect_archive(archive)
            self.assertEqual(list(inventory['complete_table_groups']), ['scheme'])

    def test_never_mix_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive=self.archive(Path(tmp), ['a/table.mu','b/table.down','b/table.up'])
            self.assertEqual(fetch.inspect_archive(archive)['complete_table_groups'], {})

    def test_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive=self.archive(Path(tmp), ['../table.mu'])
            with self.assertRaises(ValueError): fetch.inspect_archive(archive)

    def test_network_failure_recorded_without_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'attempt'
            with mock.patch.object(fetch.urllib.request,'urlopen',side_effect=OSError('offline')):
                record=fetch.fetch(output)
            self.assertEqual(record['status'], 'blocked')
            self.assertEqual(len(record['attempts']), 2)
            self.assertEqual([p.name for p in output.iterdir()], ['acquisition.json'])


if __name__=='__main__': unittest.main()
