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
python -m tidebound_dev.runtime.build_mac /tmp/tidebound-runtime-build ../runtime-output
```

The work directory must not contain spaces because the upstream dependency
makefiles do not quote their build paths. This restriction applies to rebuilding
the engine, not to running the game. Build downloads and compiler output stay
under that directory. The command does not install developer tools for you.

Packaging validates Intel and ARM slices, deployment targets and dependencies,
then normalizes bundle names and signs the assembled game ad hoc. Native tests
run one real read-only App Translocation launch per architecture. Downloads,
temporary and long Unicode paths remain opt-in diagnostics. Test quarantine approval is applied only
to disposable fixtures; it is not distributed. This is not notarization.

## Upstream inputs

The original archives remain offline build inputs, not alternate player runtimes:

- Upstream: https://github.com/mkxp-z/mkxp-z
- Revision: `826929eeb3ebc4b887c011604919217a790770f4`, dev branch.
- Official workflow run: https://github.com/mkxp-z/mkxp-z/actions/runs/28475006907
- Artifact: `7993949899`, `mkxp-z.macos.dev-826929e`.
- Outer artifact SHA256: `488c51601ca9028513c92ece43c5dff87e956219067fad1450f33ccdea81625f`.
- `mkxp-z-826929e.zip` is the unchanged inner `Z-universal.app.zip` from that artifact.
  The rebuild uses its libraries and Ruby standard library as the template.
- `mkxp-z-826929e-source.tar.gz` contains matching upstream source, build recipes
  and dependency patches. The rebuild applies `portable-launch.patch` to it.
- Runtime reports mkxp-z 2.4.2; Ruby is 3.1. Essentials originally targets the
  older c9378cf build. Windows keeps its original executable. No Essentials
  engine upgrade was performed.

The original `LICENSE.mkxp-z-with-https.txt` is retained in the app. Dependency
source URLs and versions are recorded in the source archive's macos/Dependencies
recipes. Upstream source is also at:
https://github.com/mkxp-z/mkxp-z/tree/826929eeb3ebc4b887c011604919217a790770f4

`macho_report.json` retains the historical Intel inspection of the original upstream
template; it does not describe the current patched universal player.

Packaging inspects the actual runtime and records both architectures' Mach-O
metadata in each build manifest. See [releasing](../releasing.md) for current
packaging, signing and native verification requirements.
