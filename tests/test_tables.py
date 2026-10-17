import hashlib
import io
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest


class TableInstallerTests(unittest.TestCase):
    def test_hash_and_path_safety(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            archive=root/'test.tar.gz'
            with tarfile.open(archive,'w:gz') as out:
                for name in ['table.mu','table.down','table.up']:
                    entry=tarfile.TarInfo('../../'+name)
                    data=b'SYNTHETIC INSTALLER TEST ONLY\n'
                    entry.size=len(data)
                    out.addfile(entry,io.BytesIO(data))
            script=Path(__file__).parents[1]/'scripts/stage_tables.py'
            output=root/'tables'
            command=[sys.executable,str(script),str(archive),'--output',str(output),'--sha256']
            bad=subprocess.run(command+['0'*64],capture_output=True)
            self.assertNotEqual(bad.returncode,0)
            self.assertFalse(output.exists())
            good=subprocess.run(command+[hashlib.sha256(archive.read_bytes()).hexdigest()],capture_output=True)
            self.assertEqual(good.returncode,0,good.stderr)
            self.assertEqual(sorted(p.name for p in output.iterdir()),
                             ['provenance.json','table.down','table.mu','table.up'])
            # These are parser fixtures, never physics inputs.
            self.assertFalse((root/'table.mu').exists())


if __name__=='__main__': unittest.main()
