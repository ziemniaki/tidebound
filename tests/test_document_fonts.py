from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from document_fonts import resolve_fonts


class DocumentFontTests(unittest.TestCase):
    def test_native_font_families_work_without_linux_paths(self):
        families = {'mac': ['Times New Roman.ttf', 'Times New Roman Bold.ttf', 'Times New Roman Italic.ttf',
                            'Times New Roman Bold Italic.ttf', 'Arial.ttf', 'Arial Bold.ttf'],
                    'windows': ['times.ttf', 'timesbd.ttf', 'timesi.ttf', 'timesbi.ttf', 'arial.ttf', 'arialbd.ttf']}
        for system, names in families.items():
            with self.subTest(system=system), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                roots = {name: root / name for name in ('linux', 'mac', 'windows')}
                roots[system].mkdir()
                for name in names:
                    (roots[system] / name).touch()
                found = resolve_fonts(**roots)
                self.assertEqual(set(found.values()), {roots[system] / name for name in names})
                (roots[system] / names[1]).unlink()
                with self.assertRaisesRegex(RuntimeError, 'fonts are missing'):
                    resolve_fonts(**roots)
