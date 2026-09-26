# Native Mac runtime

## Current packaging — portable1

The upstream base remains `826929eeb3ebc4b887c011604919217a790770f4`.
`portable-launch.patch` changes Mac path resolution, removes the Downloads
restriction and replaces the 512-byte bundle-path buffer. The rebuilt template
replaces only `Contents/MacOS/Z-universal`; all four upstream dylibs and Ruby
standard-library files remain byte-for-byte unchanged. Gameplay is not patched.

`dependencies.lock.json` pins the engine build's dependencies, including the
SDL_image vendor snapshots. `RUNTIME_BUILD.json` records the source/template,
patch and lock hashes, Xcode version and resulting archive hashes. The patched
source archive contains the matching engine source, patch and dependency lock.
`release.json` pins the distributable runtime and source archives.

Rebuild on a Mac with Xcode and autoconf, automake, libtool, cmake and pkg-config:

```sh
python Development/rebuild_mac_runtime.py /tmp/tidebound-runtime-build ../runtime-output
```

The work directory must not contain spaces because the upstream dependency
makefiles do not quote their build paths. This restriction applies to rebuilding
the engine, not to running the game. Build downloads and compiler output stay
under that directory. The command does not install developer tools for you.

Packaging validates Intel and ARM slices, deployment targets and dependencies,
then normalizes bundle names and signs the assembled game ad hoc. Native tests
exercise Downloads, temporary and long Unicode paths, and real read-only App
Translocation on both architectures. Test quarantine approval is applied only
to disposable fixtures; it is not distributed. This is not notarization.

## Historical input provenance

Game release: 0.3.0. Packaging date: 9 September 2026.

- Upstream: https://github.com/mkxp-z/mkxp-z
- Revision: `826929eeb3ebc4b887c011604919217a790770f4`, dev branch.
- Official workflow run: https://github.com/mkxp-z/mkxp-z/actions/runs/28475006907
- Artifact: `7993949899`, `mkxp-z.macos.dev-826929e`.
- Outer artifact SHA256: `488c51601ca9028513c92ece43c5dff87e956219067fad1450f33ccdea81625f`.
- `mkxp-z-826929e.zip` is the unchanged inner `Z-universal.app.zip` from that artifact.
- Runtime reports mkxp-z 2.4.2; Ruby is 3.1. Essentials originally targets the
  older c9378cf build. Windows keeps its original executable. No Essentials
  engine upgrade was performed.

`macho_report.json` records all five Intel Mach-O images and their load commands.
The main executable, Ruby, EGL and GLES target macOS 10.13; FluidSynth targets
10.12. All linked non-system dylibs resolve inside Contents/Frameworks.
The executable uses OpenGL by default on Intel. Apple Silicon code is also
present upstream, but this release is prepared and documented for Intel.

The upstream Intel executable has no LC_CODE_SIGNATURE. This development app
is unsigned and not notarized. The packager preserves native binary bytes and
permissions, adds Contents/Game, and updates the app's name, identifier and
version. It does not disable macOS security or require a machine-wide bypass.

Matching upstream source, build recipes and dependency patches are in
`mkxp-z-826929e-source.tar.gz`. The original `LICENSE.mkxp-z-with-https.txt`
is retained in the app. Dependency source URLs and versions are recorded in
the source archive's macos/Dependencies recipes. Upstream source is also at:
https://github.com/mkxp-z/mkxp-z/tree/826929eeb3ebc4b887c011604919217a790770f4

Rebuild from the maintained project with:

```sh
python3 Development/build_release.py /path/to/new-output-folder
```

The complete game is copied into the app at packaging time. Editing the project
requires rebuilding; no runtime file inside an already downloaded app silently
synchronizes with the maintained ZIP. The stable save identity remains
`Tidebound_Opening_0_2`.

Verification separates static Mac checks, actual rendered Linux engine checks,
and native Mac testing. No native Mac playtest has been run by the agent.
