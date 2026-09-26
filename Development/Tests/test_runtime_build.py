from pathlib import Path
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rebuild_mac_runtime import SOURCE, PATCH, run
from release_tools import ROOT, load_release


class RuntimeBuildTests(unittest.TestCase):
    def test_make_pwd_matches_subprocess_working_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            run(sys.executable, '-c',
                'import os; from pathlib import Path; assert os.environ["PWD"] == str(Path.cwd())',
                cwd=Path(temp), env=dict(os.environ, PWD='/unrelated/caller'))

    def test_patch_reconstructs_the_shipped_engine_sources(self):
        config = load_release()
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            with tarfile.open(SOURCE) as original:
                original.extractall(folder, filter='data')
                top = original.getnames()[0].split('/')[0]
            subprocess.run(['git', 'apply', str(PATCH)], cwd=folder / top, check=True)
            with tarfile.open(ROOT / config['runtime_source']) as patched:
                prefix = patched.getnames()[0].split('/')[0]
                for name in ('src/main.cpp', 'src/filesystem/filesystemImplApple.mm',
                             'src/filesystem/portablePathApple.h'):
                    self.assertEqual((folder / top / name).read_bytes(), patched.extractfile(prefix + '/' + name).read())


if __name__ == '__main__':
    unittest.main()
