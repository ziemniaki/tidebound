from pathlib import Path
import hashlib
import sys
import subprocess
import shutil
import tempfile
import unittest
import zipfile
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

from tidebound_dev.runtime.inputs import unpack_pinned
from tidebound_dev.packaging.pipeline import development_settings, DEV_SAVES


class RuntimeRestorationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def archive(self, name='Game.exe'):
        path = self.root / 'runtime.zip'
        with zipfile.ZipFile(path, 'w') as z:
            z.writestr(name, b'pinned binary')
        return {'runtime': 'runtime.zip', 'runtime_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    def test_fresh_checkout_restores_offline_and_repairs_changed_cache(self):
        config = self.archive()
        restored = unpack_pinned(self.root, config, 'runtime')
        self.assertEqual((restored / 'Game.exe').read_bytes(), b'pinned binary')
        (restored / 'Game.exe').write_bytes(b'local corruption')
        self.assertEqual(unpack_pinned(self.root, config, 'runtime'), restored)
        self.assertEqual((restored / 'Game.exe').read_bytes(), b'pinned binary')

    def test_concurrent_first_restores_never_delete_a_published_cache(self):
        config = self.archive()
        start = Barrier(8)
        def restore(_):
            start.wait(timeout=10)
            result = unpack_pinned(self.root, config, 'runtime')
            self.assertEqual((result / 'Game.exe').read_bytes(), b'pinned binary')
            return result
        original = shutil.rmtree
        def remove(path, *args, **kwargs):
            self.assertNotEqual(Path(path).name, config['runtime_sha256'],
                                'a healthy published cache was removed')
            return original(path, *args, **kwargs)
        with patch('tidebound_dev.runtime.inputs.shutil.rmtree', side_effect=remove), ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(restore, range(8)))
        self.assertEqual(len(set(results)), 1)
        self.assertEqual((results[0] / 'Game.exe').read_bytes(), b'pinned binary')

    def test_changed_archive_is_rejected_before_restoring(self):
        config = self.archive()
        (self.root / 'runtime.zip').write_bytes(b'corrupt download')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            unpack_pinned(self.root, config, 'runtime')
        self.assertFalse((self.root / '.cache').exists())

    def test_archive_cannot_write_outside_cache(self):
        for name in ('../escape.exe', '/escape.exe', 'nested/Game.exe', '..\\escape.exe'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'flat filenames'):
                unpack_pinned(self.root, self.archive(name), 'runtime')


class DevelopmentSaveTests(unittest.TestCase):
    def test_only_disposable_config_gets_separate_saves(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'source'
            player = root / 'player'
            source.mkdir(); player.mkdir()
            original = '// comment\n{"dataPathApp": "Tidebound_Opening_0_2", "fontHeightReporting": 1}'
            for folder in (source, player):
                (folder / 'mkxp.json').write_text(original)
            development_settings(player)
            self.assertEqual((source / 'mkxp.json').read_text(), original)
            self.assertEqual((player / 'mkxp.json').read_text(), original.replace('Tidebound_Opening_0_2', DEV_SAVES))

    def test_missing_or_ambiguous_save_setting_fails_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for original in ('{}', '{"dataPathApp":"a", "dataPathApp":"b"}'):
                (root / 'mkxp.json').write_text(original)
                with self.assertRaisesRegex(ValueError, 'exactly one'):
                    development_settings(root)
                self.assertEqual((root / 'mkxp.json').read_text(), original)
