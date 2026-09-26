"""Explicitly refresh an unpublished draft after full CI, retaining a backup."""
from pathlib import Path
import json
import os
import re
import subprocess
import sys

from release_tools import load_release, sha256
from verify_artifacts import verify


def command(*args):
    return subprocess.check_output(args, text=True).strip()


def api(path, data=None):
    args = ['gh', 'api', '--method', 'GET' if data is None else 'PATCH', path]
    if data is not None:
        args += ['--input', '-']
    return json.loads(subprocess.check_output(args, input=None if data is None else json.dumps(data), text=True))


def validate_draft(release, tag, actual_sha, expected_sha):
    if (release.get('draft') is not True or release.get('published_at') is not None or
            release.get('immutable') or release.get('tag_name') != tag):
        raise ValueError('Only the matching unpublished, mutable draft can be refreshed')
    if not re.fullmatch(r'[0-9a-f]{40}', expected_sha) or actual_sha != expected_sha:
        raise ValueError('Tag changed or expected tag SHA is invalid; refusing to retag')


def asset_snapshot(release):
    return sorted((a['id'], a['name'], a['size'], a.get('digest')) for a in release['assets'])


def check(repo, tag, expected):
    pages = json.loads(command('gh', 'api', '--paginate', '--slurp', f'repos/{repo}/releases?per_page=100'))
    matches = [r for page in pages for r in page if r['tag_name'] == tag]
    if len(matches) != 1:
        raise ValueError('Expected exactly one existing release for ' + tag)
    release = matches[0]
    ref = api(f'repos/{repo}/git/ref/tags/{tag}')
    validate_draft(release, tag, ref['object']['sha'], expected)
    return release, ref


def validate_candidate(folder, version, commit, mac_build):
    verify(folder)
    expected = {f'Tidebound_Mac_{version}_universal.zip', f'Tidebound_Windows_{version}_x64.zip',
                f'Tidebound_Linux_{version}_x86_64.zip', f'Tidebound_Project_{version}.zip',
                'BUILD.json', 'WINDOWS_BUILD.json', 'LINUX_BUILD.json', 'SHA256SUMS.txt', 'RELEASE_NOTES.md'}
    if {p.name for p in folder.iterdir()} != expected:
        raise ValueError('Expected the complete four-platform/project candidate set')
    for name in ('BUILD.json', 'WINDOWS_BUILD.json', 'LINUX_BUILD.json'):
        manifest = json.loads((folder / name).read_text())
        if manifest['version'] != version or manifest['source'] != {'commit': commit, 'dirty': False}:
            raise ValueError('Candidate source/version does not match verified workflow commit')
    if json.loads((folder / 'BUILD.json').read_text())['mac_build'] != mac_build:
        raise ValueError('Candidate Mac build does not match release metadata')


def main(mode, folder=None):
    if os.environ['GITHUB_REF'] != 'refs/heads/main':
        raise ValueError('Draft refresh must be dispatched on main')
    repo = os.environ['GITHUB_REPOSITORY']
    expected = os.environ['EXPECTED_TAG_SHA']
    source = os.environ['GITHUB_SHA']
    if command('git', 'rev-parse', 'HEAD') != source:
        raise ValueError('Checkout does not match workflow source')
    config = load_release()
    tag = 'v' + config['version']
    release, ref = check(repo, tag, expected)
    if mode == 'check':
        print('Validated draft', release['id'], 'and current tag', expected)
        return
    folder = Path(folder).resolve()
    backup = Path(os.environ['RUNNER_TEMP']) / 'previous-release'
    validate_candidate(folder, config['version'], source, config['mac_build'])
    if any(a['name'] not in {p.name for p in folder.iterdir()} for a in release['assets']):
        raise ValueError('Draft has extra assets; refusing to silently discard them')
    if mode == 'backup':
        backup.mkdir()
        subprocess.run(['gh', 'release', 'download', tag, '--repo', repo, '--dir', str(backup)], check=True)
        for asset in release['assets']:
            if asset.get('digest') != 'sha256:' + sha256(backup / asset['name']):
                raise ValueError('Previous release backup checksum mismatch')
        (backup / 'PREVIOUS_RELEASE.json').write_text(json.dumps(release, indent=2) + '\n')
        (backup / 'PREVIOUS_TAG.json').write_text(json.dumps(ref, indent=2) + '\n')
        print('Backed up all previous draft assets and metadata')
        return
    if mode != 'refresh':
        raise ValueError('Expected check, backup or refresh')
    previous = json.loads((backup / 'PREVIOUS_RELEASE.json').read_text())
    if previous['id'] != release['id'] or asset_snapshot(previous) != asset_snapshot(release):
        raise ValueError('Draft assets changed since backup')
    for asset in previous['assets']:
        if asset['digest'] != 'sha256:' + sha256(backup / asset['name']):
            raise ValueError('Backup changed before refresh')
    # The Actions token prevents a recursive tag-triggered build. The full build
    # is already a required predecessor of this job. The lease protects the tag
    # against another writer changing it between validation and push.
    subprocess.run(['gh', 'auth', 'setup-git'], check=True)
    subprocess.run(['git', 'push', f'--force-with-lease=refs/tags/{tag}:{expected}',
                    'origin', f'{source}:refs/tags/{tag}'], check=True)
    subprocess.run(['gh', 'release', 'upload', tag, '--repo', repo, '--clobber',
                    *[str(p) for p in sorted(folder.iterdir())]], check=True)
    api(f"repos/{repo}/releases/{release['id']}", {
        'draft': True, 'target_commitish': source,
        'body': (folder / 'RELEASE_NOTES.md').read_text()})
    current, _ = check(repo, tag, source)
    actual = {a['name']: a.get('digest') for a in current['assets']}
    hashes = {p.name: 'sha256:' + sha256(p) for p in folder.iterdir()}
    if actual != hashes:
        raise ValueError('Refreshed draft assets do not match the verified candidate')
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
        summary.write(f"Refreshed [{tag}]({current['html_url']}) at `{source}`; still unpublished.\n")
    print('PASS: complete refreshed draft, tag and all asset hashes verified')


if __name__ == '__main__':
    main(*sys.argv[1:])
