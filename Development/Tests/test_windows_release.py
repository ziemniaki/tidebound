from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from package_windows import RUNTIME_FILES, build, inspect_runtime
from release_tools import sha256
from verify_artifacts import verify
from smoke_report import read_report


class WindowsReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'source'
        self.root.mkdir()
        self.output = self.base / 'release'
        # Minimal PE header; these fixtures are never executed.
        pe = bytearray(160)
        pe[:2] = b'MZ'
        struct.pack_into('<I', pe, 0x3c, 64)
        pe[64:68] = b'PE\0\0'
        pe[68:70] = b'\x64\x86'
        pe[88:90] = b'\x0b\x02'
        for name in RUNTIME_FILES:
            (self.root / name).write_bytes(pe)
        self.config = {'version': '1.2.3', 'windows_runtime_sha256':
                       {name: sha256(self.root / name) for name in RUNTIME_FILES}}
        for name in ('Game.ini', 'mkxp.json', 'soundfont.sf2', 'CREDITS.md',
                     'WINDOWS_README.txt', 'Runtime/Windows/PROVENANCE.md',
                     'Data/Scripts.rxdata', 'Development/private.txt', '.venv/cache'):
            file = self.root / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(b'fixture')
        for name, value in [('check_sources', self.config),
                            ('source_revision', {'commit': 'a' * 40, 'dirty': False})]:
            patcher = patch('package_windows.' + name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch('package_windows.subprocess.run')
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_player_zip_excludes_development_files_and_preserves_runtime(self):
        archive = build(self.output, self.root)
        with zipfile.ZipFile(archive) as z:
            prefix = 'Tidebound_Windows_1.2.3_x64/'
            names = {name.removeprefix(prefix) for name in z.namelist()}
            self.assertIn('Data/Scripts.rxdata', names)
            self.assertIn('README.txt', names)
            self.assertFalse(any(name.startswith(('Development/', '.venv/')) for name in names))
            for name in RUNTIME_FILES:
                self.assertEqual(z.read(prefix + name), (self.root / name).read_bytes())
            manifest = json.loads(z.read(prefix + 'BUILD.json'))
            self.assertEqual(set(manifest['files_sha256']), names - {'BUILD.json'})
        verify(self.output)

    def test_mutated_runtime_is_rejected_before_output(self):
        (self.root / 'Game.exe').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'provenance hash mismatch'):
            build(self.output, self.root)
        self.assertFalse(self.output.exists())

    def test_non_x64_runtime_is_rejected_even_with_updated_hash(self):
        path = self.root / 'Game.exe'
        data = bytearray(path.read_bytes())
        data[68:70] = b'\x64\xaa'  # ARM64
        path.write_bytes(data)
        self.config['windows_runtime_sha256']['Game.exe'] = sha256(path)
        with self.assertRaisesRegex(ValueError, 'x64 PE32'):
            inspect_runtime(self.root, self.config)

    def test_failed_zip_verification_cleans_staging(self):
        with patch('package_windows.extract_bundle', side_effect=ValueError('bad ZIP')):
            with self.assertRaisesRegex(ValueError, 'bad ZIP'):
                build(self.output, self.root)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.base.glob('.tidebound-windows-*')), [])

    def test_existing_release_is_preserved(self):
        self.output.mkdir()
        (self.output / 'keep').write_text('existing')
        with self.assertRaises(FileExistsError):
            build(self.output, self.root)
        self.assertEqual((self.output / 'keep').read_text(), 'existing')

    def test_download_checksum_detects_corruption_and_unlisted_files(self):
        archive = build(self.output, self.root)
        unexpected = self.output / 'unexpected.zip'
        unexpected.write_bytes(b'unknown')
        with self.assertRaisesRegex(ValueError, 'complete candidate'):
            verify(self.output)
        unexpected.unlink()
        archive.write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            verify(self.output)

    def test_native_encoded_strings_remain_readable_in_json_reports(self):
        from rubymarshal.classes import RubyString
        from rubymarshal.writer import writes
        payload = {RubyString('passed'): False, RubyString('error'): RubyString('Pokémon failure'),
                   RubyString('checks'): [RubyString('font rendering')]}
        (self.base / 'native-smoke.rxdata').write_bytes(writes(payload))
        result = read_report(self.base)
        self.assertEqual(result, {'passed': False, 'error': 'Pokémon failure', 'checks': ['font rendering']})
        self.assertEqual(json.loads((self.base / 'native-smoke.json').read_text()), result)


if __name__ == '__main__':
    unittest.main()
