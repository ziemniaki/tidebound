"""Rebuild the pinned Mac engine with the portable-launch patch.

Requires macOS/Xcode plus autoconf, automake, libtool, cmake and pkg-config.
Use a build path without spaces (upstream makefiles require this). Dependencies
are pinned by commit; this command never installs or removes system packages.
"""
from pathlib import Path
import argparse
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile

from mac_runtime import inspect_runtime
from package_mac import archive_tree, extract_bundle
from release_tools import ROOT, sha256

SOURCE = ROOT / 'Runtime/macOS/mkxp-z-826929e-source.tar.gz'
SOURCE_SHA = '87f70b4738a78fd66630312c795e760f59def7fcff0dfe12c2d50bd7ec65e21b'
PATCH = ROOT / 'Runtime/macOS/portable-launch.patch'
LOCK = ROOT / 'Runtime/macOS/dependencies.lock.json'
TEMPLATE = ROOT / 'Runtime/macOS/mkxp-z-826929e.zip'
TEMPLATE_SHA = 'b065fd4f5ea77a5b8f8dc736842e55349d7b344b7c2438b175e9cb589d5476fb'


def run(*args, cwd=None, env=None, log=None):
    # Upstream makefiles use $PWD instead of make's CURDIR. subprocess cwd
    # alone leaves the parent's exported PWD pointing at the caller's checkout.
    if cwd is not None:
        env = dict(os.environ if env is None else env, PWD=str(Path(cwd).resolve()))
    subprocess.run([str(a) for a in args], cwd=cwd, env=env, stdout=log,
                   stderr=subprocess.STDOUT if log else None, check=True)


def fetch(folder, info, log):
    if not (folder / '.git').exists():
        folder.mkdir(parents=True, exist_ok=True)
        run('git', 'init', '-q', folder, log=log)
        run('git', '-C', folder, 'remote', 'add', 'origin', info['url'], log=log)
        run('git', '-C', folder, 'fetch', '--depth', '1', 'origin', info['commit'], log=log)
        run('git', '-C', folder, 'checkout', '--detach', 'FETCH_HEAD', log=log)
    head = subprocess.check_output(['git', '-C', str(folder), 'rev-parse', 'HEAD'], text=True).strip()
    if head != info['commit']:
        raise ValueError('Cached dependency commit differs from lock: ' + str(folder))
    if 'submodules' in info:
        for name, child in info['submodules'].items():
            fetch(folder / name, child, log)
    elif (folder / '.gitmodules').exists():
        run('git', 'submodule', 'update', '--init', '--recursive', cwd=folder, log=log)


def build_arch(source, arch, jobs):
    deps = source / 'macos/Dependencies'
    host = ('aarch64' if arch == 'arm64' else arch) + '-apple-darwin'
    downloads = deps / 'downloads' / host
    prefix = deps / ('build-macosx-' + arch)
    minimum = '11.0' if arch == 'arm64' else '10.13'
    with (source.parent / ('build-' + arch + '.log')).open('a') as log:
        for name, info in json.loads(LOCK.read_text()).items():
            fetch(downloads / name, info, log)
        ruby = downloads / 'ruby/configure.ac'
        text = ruby.read_text().replace(': ${PRELOADENV=DYLD_INSERT_LIBRARIES}', '')
        if text != ruby.read_text():
            ruby.write_text(text)
        # A host Ruby/Homebrew default can otherwise redirect gem installation
        # outside --prefix. Scope the bootstrap install to the build tree.
        installer = downloads / 'ruby/tool/rbinstall.rb'
        text = installer.read_text().replace('gem_dir = Gem.default_dir',
            'gem_dir = File.join(RbConfig::CONFIG["libdir"], "ruby", "gems", RbConfig::CONFIG["ruby_version"])')
        if text != installer.read_text():
            installer.write_text(text)
        # Freetype ships a dispatcher Makefile; its presence must not skip the
        # actual configure step when pre-fetching pinned sources.
        freetype = downloads / 'freetype'
        if not (freetype / 'builds/unix/unix-def.mk').exists():
            run('./autogen.sh', cwd=freetype, log=log)
            env = dict(os.environ, MACOSX_DEPLOYMENT_TARGET=minimum, CC='clang -arch ' + arch,
                       CFLAGS=f'-I{prefix}/include -I{prefix}/include/freetype2 -mmacosx-version-min={minimum} -O3',
                       LDFLAGS=f'-L{prefix}/lib', PKG_CONFIG_LIBDIR=str(prefix / 'lib/pkgconfig'))
            # Build its pinned libpng dependency before configuration.
            run('make', '-f', arch + '.make', 'libpng', 'NPROC=' + str(jobs), cwd=deps, log=log)
            run('./configure', '--prefix=' + str(prefix), '--host=' + host,
                '--enable-static=true', '--enable-shared=false', cwd=freetype, env=env, log=log)
        run('make', '-f', arch + '.make', 'everything', 'NPROC=' + str(jobs), cwd=deps, log=log)


def build(work, output, jobs):
    if sys.platform != 'darwin':
        raise ValueError('A native Mac/Xcode host is required')
    work, output = work.resolve(), output.resolve()
    if any(c.isspace() for c in str(work)):
        raise ValueError('Upstream dependency makefiles require a work path without spaces')
    if output.exists():
        raise FileExistsError('Choose a new runtime output directory')
    if sha256(SOURCE) != SOURCE_SHA or sha256(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError('Upstream source archive checksum mismatch')
    stamp = {'source': SOURCE_SHA, 'template': TEMPLATE_SHA, 'patch': sha256(PATCH), 'dependencies': sha256(LOCK)}
    work.mkdir(parents=True, exist_ok=True)
    marker = work / 'inputs.json'
    if marker.exists() and json.loads(marker.read_text()) != stamp:
        raise ValueError('Build inputs changed; choose a fresh work directory')
    with tarfile.open(SOURCE) as archive:
        top = archive.getnames()[0].split('/')[0]
        source = work / top
        if not source.exists():
            archive.extractall(work, filter='data')
            run('patch', '-p1', '-i', PATCH, cwd=source)
            marker.write_text(json.dumps(stamp, indent=2) + '\n')
        elif not marker.exists():
            raise ValueError('Refusing to reuse an untracked source/build directory')
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda arch: build_arch(source, arch, jobs), ['arm64', 'x86_64']))
    run('/usr/bin/ruby', 'make_macuniversal.sh', cwd=source / 'macos/Dependencies')
    with (work / 'xcode.log').open('w') as log:
        run('xcodebuild', '-project', 'mkxp-z.xcodeproj', '-configuration', 'Release',
            '-scheme', 'Universal', '-derivedDataPath', work / 'xcode',
            'CODE_SIGNING_ALLOWED=NO', cwd=source / 'macos', log=log)
    app = work / 'xcode/Build/Products/Release/Z-universal.app'
    export_runtime(source, app, work, output, stamp)


def export_runtime(source, app, work, output, stamp):
    if output.exists():
        raise FileExistsError('Choose a new runtime output directory')
    top = source.name
    final_output = output
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.runtime-artifacts-', dir=output.parent) as staging:
        output = Path(staging) / 'artifacts'
        output.mkdir(parents=True)
        with tempfile.TemporaryDirectory(prefix='runtime-template-', dir=work) as temp:
            stage = Path(temp)
            extract_bundle(TEMPLATE, stage)
            template = stage / 'Z-universal.app'
            # Only the engine executable changes. Retain the original Ruby, ANGLE,
            # FluidSynth and standard library to avoid unrelated runtime changes.
            shutil.copy2(app / 'Contents/MacOS/Z-universal', template / 'Contents/MacOS/Z-universal')
            inspect_runtime(template, ['x86_64', 'arm64'])
            archive_tree(template, output / 'mkxp-z-826929e-portable1.zip')
        # Include exactly the upstream source members, their patched replacements,
        # the new header and the dependency lock. Never archive build caches.
        with tarfile.open(SOURCE) as original, tarfile.open(output / 'mkxp-z-826929e-portable1-source.tar.gz', 'w:gz') as result:
            for member in original.getmembers():
                result.add(source / Path(member.name).relative_to(top), arcname=member.name, recursive=False)
            result.add(source / 'src/filesystem/portablePathApple.h', arcname=top + '/src/filesystem/portablePathApple.h')
            result.add(LOCK, arcname=top + '/tidebound-dependencies.lock.json')
            result.add(PATCH, arcname=top + '/tidebound-portable-launch.patch')
        stamp['toolchain'] = subprocess.check_output(['xcodebuild', '-version'], text=True).strip()
        stamp['artifacts'] = {p.name: sha256(p) for p in output.iterdir()}
        (output / 'RUNTIME_BUILD.json').write_text(json.dumps(stamp, indent=2) + '\n')
        output.rename(final_output)
        print('Built and inspected pinned universal runtime:', final_output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('work', type=Path, help='Persistent build/cache directory without spaces')
    parser.add_argument('output', type=Path, help='New directory for verified runtime archives')
    parser.add_argument('--jobs', type=int, default=4, help='Compiler jobs per architecture')
    args = parser.parse_args()
    build(args.work, args.output, args.jobs)
