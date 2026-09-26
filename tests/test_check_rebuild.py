"""A clean regeneration must reproduce the complete set of tracked outputs."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import check_rebuild


class GeneratedFileSetTests(unittest.TestCase):
    def regenerate(self, code):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'tools').mkdir()
            (root / 'tools/generate.py').write_text(code)
            (root / 'tools/validate_maps.py').write_text('# fixture validation\n')
            subprocess.run(['git', 'init', '-q', root], check=True)
            subprocess.run(['git', '-C', root, 'add', '.'], check=True)
            with patch.object(check_rebuild, 'ROOT', root), patch.object(check_rebuild, 'GENERATORS', ('generate.py',)), redirect_stdout(StringIO()):
                check_rebuild.main()

    def test_new_untracked_output_cannot_pass_regeneration(self):
        with self.assertRaisesRegex(SystemExit, 'new-sprite.png'):
            self.regenerate("from pathlib import Path\nPath('new-sprite.png').write_bytes(b'new generated asset')\n")

    def test_python_import_cache_is_not_a_generated_game_asset(self):
        self.regenerate("from pathlib import Path\np=Path('tools/__pycache__');p.mkdir();(p/'fixture.pyc').write_bytes(b'cache')\n")
