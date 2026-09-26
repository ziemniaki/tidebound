"""Map imports and isolated builders must not depend on execution order."""
from pathlib import Path
import importlib
import pkgutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from tidebound_dev import maps
from tidebound_dev.maps import areas, compiler


class MapBuilderTests(unittest.TestCase):
    def test_modules_import_without_loading_or_writing_game_assets(self):
        with patch('PIL.Image.open', side_effect=AssertionError('image read during import')), \
             patch('PIL.Image.Image.save', side_effect=AssertionError('image write during import')), \
             patch.object(Path, 'write_bytes', side_effect=AssertionError('binary write during import')), \
             patch.object(Path, 'write_text', side_effect=AssertionError('text write during import')):
            for module in pkgutil.iter_modules(maps.__path__, maps.__name__ + '.'):
                importlib.reload(importlib.import_module(module.name))

    def test_one_area_can_be_built_without_constructing_another(self):
        with patch.object(areas, 'build_coast', side_effect=AssertionError('unrelated area')):
            first = areas.build_home()
            second = areas.build_home()
        self.assertEqual(first.serialize(), second.serialize())
        first.layers[0][3][3] = 0
        first.events.clear()
        self.assertNotEqual(first.serialize(), second.serialize())
        self.assertTrue(second.events)

    def test_validation_failure_does_not_publish_any_generated_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'game/Data').mkdir(parents=True)
            original = root / 'game/Data/Map101.rxdata'
            original.write_bytes(b'original')

            def failed_output(paths, _maps):
                (paths.game / 'Data/Map101.rxdata').write_bytes(b'changed')
                (paths.root / 'src/generated/map_passages.rb').write_text('changed')

            with patch.object(compiler, 'construct', return_value=[]), \
                 patch.object(compiler, 'serialize', side_effect=failed_output), \
                 patch('tidebound_dev.maps.validate.validate', side_effect=ValueError('blocked transfer')):
                with self.assertRaisesRegex(ValueError, 'blocked transfer'):
                    compiler.build(root)
            self.assertEqual(original.read_bytes(), b'original')
            self.assertFalse((root / 'src').exists())
            self.assertFalse((root / 'tools').exists())


if __name__ == '__main__':
    unittest.main()
