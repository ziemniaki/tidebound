from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from refresh_draft import validate_candidate, validate_draft
from release_tools import sha256


class DraftRefreshTests(unittest.TestCase):
    def test_published_or_immutable_release_is_never_refreshable(self):
        for change in ({'draft': False}, {'published_at': '2026-09-26'}, {'immutable': True}, {'tag_name': 'v0.8.4'}):
            release = dict(draft=True, published_at=None, immutable=False, tag_name='v0.8.5')
            release.update(change)
            with self.assertRaisesRegex(ValueError, 'unpublished'):
                validate_draft(release, 'v0.8.5', 'a' * 40, 'a' * 40)

    def test_tag_must_still_match_the_explicit_lease(self):
        release = dict(draft=True, published_at=None, immutable=False, tag_name='v0.8.5')
        with self.assertRaisesRegex(ValueError, 'Tag changed'):
            validate_draft(release, 'v0.8.5', 'b' * 40, 'a' * 40)
        validate_draft(release, 'v0.8.5', 'a' * 40, 'a' * 40)

    def test_candidate_cannot_mix_commits_or_omit_linux(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            for platform in ('Mac_0.8.5_universal', 'Windows_0.8.5_x64', 'Linux_0.8.5_x86_64', 'Project_0.8.5'):
                (folder / ('Tidebound_' + platform + '.zip')).write_bytes(b'verified by build gate')
            manifest = {'version': '0.8.5', 'mac_build': '40', 'source': {'commit': 'a' * 40, 'dirty': False}}
            for name in ('BUILD.json', 'WINDOWS_BUILD.json', 'LINUX_BUILD.json'):
                (folder / name).write_text(json.dumps(manifest))
            (folder / 'RELEASE_NOTES.md').write_text('notes')

            def checksums():
                (folder / 'SHA256SUMS.txt').write_text(''.join(
                    sha256(p) + '  ' + p.name + '\n' for p in sorted(folder.iterdir()) if p.name != 'SHA256SUMS.txt'))

            checksums()
            validate_candidate(folder, '0.8.5', 'a' * 40, '40')
            with self.assertRaisesRegex(ValueError, 'source/version'):
                validate_candidate(folder, '0.8.5', 'b' * 40, '40')
            with self.assertRaisesRegex(ValueError, 'Mac build'):
                validate_candidate(folder, '0.8.5', 'a' * 40, '39')
            (folder / 'Tidebound_Linux_0.8.5_x86_64.zip').unlink()
            checksums()
            with self.assertRaisesRegex(ValueError, 'complete'):
                validate_candidate(folder, '0.8.5', 'a' * 40, '40')


if __name__ == '__main__':
    unittest.main()
