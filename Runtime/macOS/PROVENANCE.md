# Native Mac runtime

## Current packaging

The checked-in template and source archives remain unchanged. `release.json`
pins their SHA-256 values. The template contains both `x86_64` and `arm64` in
the executable and all four libraries. The current Mac packager validates both
architectures, deployment targets and bundled dependencies, then ad-hoc signs
the assembled app and verifies its ZIP roundtrip. It preserves the engine code;
signature bytes change. The upstream license moves from the bundle root to
`Contents/Resources/LICENSE.mkxp-z-with-https.txt`; the source archive remains
beside the app. This is not Developer ID signing or notarization.

See [the release workflow](../../Development/RELEASING.md) for commands and the
distinction between static inspection, native smoke and target-device playtesting.
The report below records the original Intel inspection, not the new universal
package's signatures or ARM test results.

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
