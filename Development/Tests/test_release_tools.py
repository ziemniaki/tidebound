from pathlib import Path
import json
import plistlib
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_rebuild import equivalent
from package_mac import archive_tree, build, extract_bundle, game_hashes, normalize_bundle_names
from release_tools import ROOT, check_sources, load_release, source_revision


class ArchiveSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / 'input.zip'
        self.out = self.root / 'out'
        self.out.mkdir()

    def test_parent_traversal_is_rejected(self):
        with zipfile.ZipFile(self.archive, 'w') as archive:
            archive.writestr('../outside', 'bad')
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            extract_bundle(self.archive, self.out)
        self.assertFalse((self.root / 'outside').exists())

    def test_escaping_symlink_is_rejected(self):
        link = zipfile.ZipInfo('escape')
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(self.archive, 'w') as archive:
            archive.writestr(link, '../outside')
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            extract_bundle(self.archive, self.out)

    def test_duplicate_archive_member_is_rejected(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(self.archive, 'w') as archive:
                archive.writestr('same', 'first')
                archive.writestr('same', 'second')
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            extract_bundle(self.archive, self.out)

    def test_zip_roundtrip_preserves_links_and_executable_bits(self):
        folder = self.root / 'bundle'
        folder.mkdir()
        (folder / 'engine').write_bytes(b'runtime')
        (folder / 'engine').chmod(0o755)
        (folder / 'alias').symlink_to('engine')
        archive_tree(folder, self.archive)
        extract_bundle(self.archive, self.out)
        self.assertTrue((self.out / 'bundle/alias').is_symlink())
        self.assertEqual((self.out / 'bundle/alias').read_bytes(), b'runtime')
        self.assertEqual((self.out / 'bundle/engine').stat().st_mode & 0o777, 0o755)

    def test_mac_filenames_survive_archive_utility_normalization(self):
        folder = self.root / 'bundle'
        audio = folder / 'Contents/Game/Audio/BGM'
        audio.mkdir(parents=True)
        (audio / 'Rout\u00e9 1.mid').write_bytes(b'audio')
        expected = game_hashes(folder, 'NFC')
        normalize_bundle_names(folder)
        archive_tree(folder, self.archive)
        with zipfile.ZipFile(self.archive) as archive:
            self.assertIn('bundle/Contents/Game/Audio/BGM/Route\u0301 1.mid', archive.namelist())
        extract_bundle(self.archive, self.out)
        self.assertEqual(game_hashes(self.out / 'bundle', 'NFC'), expected)


class BuildTransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'source'
        self.root.mkdir()
        self.output = self.root.parent / 'release'
        self.config = load_release()
        self.config.update(runtime_archive='runtime.zip', runtime_source='source.tar.gz')
        for name in ('Game.ini', 'mkxp.json', 'soundfont.sf2', 'MAC_README.txt', 'CREDITS.md',
                     'Runtime/macOS/PROVENANCE.md', 'source.tar.gz', 'Data/Scripts.rxdata',
                     'Audio/BGM/Rout\u00e9 1.mid'):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'fixture')
        with zipfile.ZipFile(self.root / 'runtime.zip', 'w') as archive:
            archive.writestr('Z-universal.app/Contents/Info.plist', plistlib.dumps({'CFBundleExecutable': 'Engine'}))
            archive.writestr('Z-universal.app/Contents/MacOS/Engine', b'fixture')
            archive.writestr('Z-universal.app/Contents/Resources/placeholder', b'fixture')
            archive.writestr('Z-universal.app/LICENSE.mkxp-z-with-https.txt', b'license')
        for name, value in [('check_sources', self.config),
                            ('source_revision', {'commit': 'a' * 40, 'dirty': False}),
                            ('inspect_runtime', [])]:
            patcher = patch('package_mac.' + name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch('subprocess.run')
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_failed_signing_never_exposes_partial_release(self):
        with patch('package_mac.sign_app', side_effect=RuntimeError('signing failed')):
            with self.assertRaisesRegex(RuntimeError, 'signing failed'):
                build(self.output, self.root)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.root.parent.glob('.tidebound-package-*')), [])

    def test_existing_output_is_preserved(self):
        self.output.mkdir()
        (self.output / 'keep').write_text('existing release')
        with self.assertRaises(FileExistsError):
            build(self.output, self.root)
        self.assertEqual((self.output / 'keep').read_text(), 'existing release')

    def test_successful_transaction_has_only_verified_artifacts(self):
        def verify_names_at_signing(app):
            names = [p.name for p in (app / 'Contents/Game/Audio/BGM').iterdir()]
            self.assertEqual(names, ['Route\u0301 1.mid'])

        with patch('package_mac.sign_app', side_effect=verify_names_at_signing), patch('mac_runtime.run'):
            result = build(self.output, self.root)
        manifest = json.loads((self.output / 'BUILD.json').read_text())
        self.assertFalse(manifest['source']['dirty'])
        self.assertEqual(manifest['architectures'], ['x86_64', 'arm64'])
        with zipfile.ZipFile(result) as archive:
            names = archive.namelist()
            self.assertTrue(any(n.endswith('Contents/Resources/LICENSE.mkxp-z-with-https.txt') for n in names))
            self.assertFalse(any(n.endswith('Tidebound.app/LICENSE.mkxp-z-with-https.txt') for n in names))
        self.assertEqual(len(list(self.output.iterdir())), 3)


class ReleaseInvariantTests(unittest.TestCase):
    def test_dirty_release_is_rejected(self):
        with patch('release_tools.subprocess.check_output', return_value=' M Game.ini\n'):
            with self.assertRaisesRegex(ValueError, 'clean checkout'):
                source_revision()

    def test_runtime_hash_mismatch_is_rejected(self):
        with patch('release_tools.sha256', return_value='0' * 64):
            with self.assertRaisesRegex(ValueError, 'provenance hash'):
                check_sources()

    def test_release_version_must_match_embedded_game(self):
        config = load_release()
        config['version'] = '9.9.9'
        with patch('release_tools.load_release', return_value=config):
            with self.assertRaisesRegex(ValueError, 'Version mismatch'):
                check_sources()

    def test_png_comparison_ignores_compression_but_detects_changed_pixels(self):
        with tempfile.TemporaryDirectory() as temp:
            a, b = Path(temp) / 'a.png', Path(temp) / 'b.png'
            image = Image.new('RGBA', (8, 8), (255, 0, 0, 255))
            image.save(a, compress_level=0)
            image.save(b, compress_level=9)
            self.assertNotEqual(a.read_bytes(), b.read_bytes())
            self.assertTrue(equivalent(a, b))
            image.putpixel((0, 0), (0, 0, 0, 0))
            image.save(b)
            self.assertFalse(equivalent(a, b))


if __name__ == '__main__':
    unittest.main()
