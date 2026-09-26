from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from package_linux import build, inspect_runtime
from package_mac import extract_bundle
from release_tools import sha256
from verify_artifacts import verify


class LinuxReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'source'
        self.root.mkdir()
        self.output = self.base / 'release'
        elf = bytearray(64)
        elf[:7] = b'\x7fELF\x02\x01\x01'
        struct.pack_into('<H', elf, 18, 62)
        self.elf = elf
        archive = self.root / 'runtime.zip'
        with zipfile.ZipFile(archive, 'w') as z:
            for name in ('mkxp-z.x86_64', 'lib64/libruby.so.3.1', 'lib64/libbsd.so.0', 'lib64/libcrypt.so.1'):
                z.writestr(name, elf)
            z.writestr('stdlib/test.rb', '# Ruby')
            z.writestr('LICENSE.mkxp-z-with-https.txt', 'license')
            z.writestr('mkxp.json', 'upstream example config must not be shipped')
        self.config = {'version': '1.2.3', 'linux_runtime_archive': 'runtime.zip',
                       'linux_runtime_sha256': sha256(archive), 'linux_architecture': 'x86_64',
                       'linux_glibc_minimum': '2.35', 'runtime_commit': 'a' * 40,
                       'runtime_source': 'source.tar.gz', 'runtime_source_sha256': 'b' * 64}
        for name in ('Game.ini', 'mkxp.json', 'soundfont.sf2', 'CREDITS.md', 'LINUX_README.txt',
                     'Runtime/Linux/PROVENANCE.md', 'source.tar.gz', 'Data/Scripts.rxdata',
                     'Development/private.txt', '.venv/cache'):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'fixture')
        for name, value in [('check_sources', self.config),
                            ('source_revision', {'commit': 'a' * 40, 'dirty': False})]:
            patcher = patch('package_linux.' + name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch('package_linux.subprocess.run')
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_player_archive_preserves_runtime_game_and_launch_permissions(self):
        archive = build(self.output, self.root)
        out = self.base / 'unpacked'
        out.mkdir()
        extract_bundle(archive, out)
        game = out / 'Tidebound_Linux_1.2.3_x86_64'
        self.assertEqual((game / 'mkxp-z.x86_64').read_bytes(), self.elf)
        self.assertEqual((game / 'mkxp.json').read_bytes(), b'fixture')
        self.assertFalse((game / 'Development').exists())
        self.assertFalse((game / '.venv').exists())
        for name in ('Tidebound.sh', 'mkxp-z.x86_64'):
            self.assertEqual((game / name).stat().st_mode & 0o777, 0o755)
        manifest = json.loads((game / 'BUILD.json').read_text())
        self.assertIn('source.tar.gz', manifest['files_sha256'])
        self.assertIn('stdlib/test.rb', manifest['files_sha256'])
        verify(self.output)

    def test_changed_archive_is_rejected_before_packaging(self):
        (self.root / 'runtime.zip').write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'provenance hash'):
            build(self.output, self.root)
        self.assertFalse(self.output.exists())

    def test_wrong_elf_architecture_is_rejected(self):
        runtime = self.base / 'runtime'
        runtime.mkdir()
        extract_bundle(self.root / 'runtime.zip', runtime)
        struct.pack_into('<H', self.elf, 18, 183)
        (runtime / 'mkxp-z.x86_64').write_bytes(self.elf)
        with self.assertRaisesRegex(ValueError, 'x86_64 ELF'):
            inspect_runtime(runtime)

    def test_incomplete_runtime_never_exposes_a_release(self):
        with patch('package_linux.inspect_runtime', side_effect=ValueError('missing library')):
            with self.assertRaisesRegex(ValueError, 'missing library'):
                build(self.output, self.root)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.base.glob('.tidebound-linux-*')), [])


if __name__ == '__main__':
    unittest.main()
