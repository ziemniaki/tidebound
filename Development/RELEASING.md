# Verified builds and releases

The current workflow produces one universal Mac ZIP (native `x86_64` and `arm64`),
a Windows x64 player ZIP, a Linux x86_64 player ZIP, and an editable project ZIP. `release.json`
defines the package version, Mac build number and pinned runtime archive/source
hashes, including all three existing Windows native binaries. Existing release downloads are not replaced by tooling changes; publish a new version to distribute these updates.

## Developer commands

Install the dependencies in [README.md](README.md), then use the virtual
environment from the repository root:

```sh
python Development/verify.py
python Development/check_rebuild.py
```

The second command copies tracked files to a disposable directory, runs the map,
item, encounter, regional-species and script generators, and compares their
outputs. Binary game data must match byte-for-byte; PNGs must have identical
decoded RGBA pixels. It never runs generators in your checkout. Stage newly
added build sources before running it so they are included in the tracked copy.

On a Mac with Xcode command-line tools installed:

```sh
python Development/build_release.py ../candidate
python Development/Tests/mac_runtime_smoke.py ../candidate/Tidebound_Mac_0.8.6_universal.zip ../smoke-arm64 --arch arm64
```

For a Windows-only package, on any development host:

```sh
python Development/package_windows.py ../windows-candidate
```

On Windows x64, test that archive using:

```powershell
python Development/verify_artifacts.py ../windows-candidate
python Development/Tests/windows_runtime_smoke.py ../windows-candidate/Tidebound_Windows_0.8.6_x64.zip ../smoke-windows
```

The Windows ZIP contains the unchanged `Game.exe`, Ruby/zlib DLLs, game assets,
configuration, credits and player instructions. It excludes development sources
and editor tools. `WINDOWS_BUILD.json` records runtime and file hashes; the same
manifest is included as `BUILD.json` inside the ZIP. Packaging checks pinned
runtime hashes and x64 PE headers, all copied files, and an extraction roundtrip.
It uses the same staging/no-overwrite rules as the Mac package and accepts
`--allow-dirty` only for a local preview.

For a Linux-only package, on any development host:

```sh
python Development/package_linux.py ../linux-candidate
```

On Linux x86_64 with the libraries in `LINUX_README.txt` installed:

```sh
python Development/verify_artifacts.py ../linux-candidate
python Development/Tests/linux_runtime_smoke.py ../linux-candidate/Tidebound_Linux_0.8.6_x86_64.zip ../smoke-linux
```

The Linux ZIP bundles the unchanged upstream executable, lib64, Ruby stdlib,
game files, a working-directory-aware `Tidebound.sh`, matching engine source,
license and provenance. `LINUX_BUILD.json` records architecture, source/runtime
hashes, baseline glibc and every packaged file; the same manifest is in the ZIP.
Packaging verifies ELF architecture, content hashes and executable permissions
through extraction. The runtime targets x86_64 Ubuntu 22.04/24.04 (glibc 2.35+),
with system libraries documented in the player README. This is not an AppImage.

Use `--arch x86_64` on an Intel Mac. Choose new output paths each time. A release
build requires a clean Git checkout and records its exact commit. For a local
Mac-only preview of uncommitted changes, use
`python Development/package_mac.py ../preview --allow-dirty`; the generated
manifest explicitly marks it dirty. Preview builds are not release candidates.

Mac signing and inspection require macOS (`codesign`, `lipo`, `otool`). Linux can
run headless and regeneration gates, but no longer produces unsigned Mac release
packages. Developers do not need Apple certificates for the current ad-hoc build.

## What is verified

1. Embedded Ruby agrees with source and load order; package versions, save
   namespace and the font-height fix agree; pinned runtime hashes match.
2. The headless suites and isolated regeneration pass before release packaging.
3. All five native images contain Intel and ARM slices. Both slices' linked
   non-system libraries resolve inside the app. Binary deployment targets remain
   at most macOS 10.13 for Intel and 11.0 for ARM; these are binary metadata, not
   a claim that every OS version has been playtested.
4. The assembled app receives an ad-hoc signature, nested code first. The upstream
   root-level license is preserved under `Contents/Resources` so the complete
   bundle can be signed. Verification covers all architectures and is repeated
   after a ZIP extraction roundtrip. Bundle filenames use decomposed Unicode
   (NFD) before signing, matching Archive Utility. The roundtrip applies that
   normalization again before verifying the original signature; Python ZIP
   extraction alone missed the `Routé 1.mid` signature failure in 0.8.5.
   Mac game-hash manifest keys use NFC for comparison with source filenames;
   asset bytes are unchanged.
   For release review, also expand a fresh ZIP with macOS Archive Utility and
   run `codesign --verify --deep --strict --all-architectures` on that app before
   launching it. This catches extraction problems separately from Gatekeeper
   trust policy. Apple documents this Unicode issue in
   [Resolving Gatekeeper Problems](https://developer.apple.com/forums/thread/706379).
5. Every packaged game file matches its source hash. The project ZIP comes from
   the exact clean Git commit. `BUILD.json` records the source commit, runtime
   provenance, architectures, signing status, dependency report and game hashes.
   `SHA256SUMS.txt` covers every release file other than itself.
6. Native smoke checks launch the packaged engine on separate Intel Mac, ARM Mac
   and Windows x64 hosts,
   load the real engine/custom scripts and compiled data, exercise a native
   Pokemon/state disk save roundtrip, and render a font/sprite frame through the
   graphics backend. Logs, JSON results and a screenshot are retained by CI.

The Mac and Windows smoke tests share `Tests/native_runtime_smoke.rb`. Each
extracts a disposable copy, changes only that copy's Main entry and
save namespace, re-signs the Mac test copy, and removes its unique save directory
afterward. The test Main never replaces the release script archive; the editable project retains test sources. The Mac test launches through Launch Services from `/`, using ordinary,
temporary, Downloads and long Unicode paths. Its final case applies an
already-approved quarantine attribute to a disposable fixture, then requires
that the reported path is an actual App Translocation mount and is read-only.
This checks location independence after approval, not Gatekeeper acceptance.
The fixture includes the normal plugin/compiler boot steps and saves through
the existing user-data directory, never inside the app. Windows and Linux
fixtures are moved to Unicode paths and launched from another directory.
Linux additionally uses a symbolic-link launcher and a read-only game tree.

The pinned `portable1` Mac runtime fixes the earlier translocation failure;
installation in Applications is optional. Its source patch and dependency lock
are described in [runtime provenance](../Runtime/macOS/PROVENANCE.md). The Mac
source gate also compiles and tests the actual patched path-normalization helper.

Packaging occurs inside a temporary sibling directory. The output directory
appears only after all package checks pass; failed attempts clean up their staging
files. Existing output paths are rejected. This protects packaging transactions;
the older individual generators still modify files in place when invoked directly.

## Pull requests and tags

`Quick checks` runs Linux headless verification and tooling/game tests on every
PR update and main push. It does not package players, regenerate all assets or
start native Mac/Windows jobs.

For full verification, a collaborator with write permission comments exactly
`/verify` on an open PR. The trusted `Requested verification` workflow resolves
that PR's current head SHA, runs the complete reusable workflow with read-only
repository access, and posts a `Full verification` commit status linking the run.
The authorization/reporting jobs never execute PR code. Review the status on the
latest commit before merging: pushing another commit requires another request.
This is a maintainer policy, not newly configured branch protection.

The Actions UI also provides `Requested verification` with a PR number (including
for forks), and `Full verification` for a selected branch/tag or explicit commit.
Use the requested workflow when a PR commit status is needed. Full runs include
Linux regeneration, all player packages, ARM Mac/Intel Mac/Windows native
smoke checks and Linux native smoke on Ubuntu 22.04 and 24.04. Tags always invoke the full workflow before drafting a release.
Main pushes only run quick checks, avoiding an automatic duplicate full matrix.
Actions are pinned to reviewed commits; build jobs never get release credentials.

The comment handler uses trusted workflow definitions from main. When changing
workflow definitions themselves, also dispatch Full verification on the reviewed
PR branch to exercise the new definitions before merging; `/verify` intentionally
does not execute PR-controlled workflows with status-writing credentials.

For the next release:

1. Update `release.json` and `Tidebound::VERSION` in `Development/001_Core.rb`.
   Increment `mac_build`, update current player/docs and the build manifest, and
   rebuild scripts. `rebuild_scripts.py` takes Essentials' version from the config.
2. Run verification/regeneration and review the resulting source changes in a PR.
   Merge only after CI passes. Perform the native target-machine playtest separately.
3. Tag the merged commit with the matching version, e.g. `v0.8.5`, and push the tag
   to the original repository. Do not retag or reuse `v0.8.4`.
4. `Prepare release` requires the tag to match the config and its commit to be
   in `main`'s history. It reruns the build and all native platform checks.
   Only then does a separate job get `contents: write` and upload a **draft**
   GitHub release with only the three player ZIPs attached. The publisher rechecks checksums and the remote tag's commit.
5. Review the attached downloads and notes, then publish the draft in GitHub.
   A draft is an unpublished release, not an automatic public announcement.

For a transient workflow failure, rerun on the same tag. If a draft already exists,
the publisher refuses to overwrite it; inspect that draft rather than silently
replacing its files. Build artifacts have 14-day retention. The one-time pond
publisher is retired; `finish_pond_release.py` is retained only as historical code.

## Explicitly refreshing an unpublished draft

Use Actions > Refresh unpublished draft only when the owner requests replacing
an existing unpublished candidate. Dispatch on main and provide the current
remote tag object SHA (`git ls-remote origin refs/tags/v0.8.5`) as the lease.
Increment the Mac build number for a replacement bundle and merge its metadata
first. This is how the owner-authorized 0.8.5 build40 refresh is prepared.

The workflow validates draft status and the existing tag, runs the entire build
and native matrix, and verifies the complete candidate's hashes and source SHA.
It downloads and verifies every old asset, retaining assets and release/tag
metadata as `previous-draft-release` for 90 days before making changes. It then
moves the tag with a force-with-lease push, uploads the three player ZIPs, removes
backed-up technical/project attachments, replaces the notes, and
verifies GitHub asset digests. The release remains a draft. The Actions token's
tag push does not recursively trigger another build; the complete build already
ran as a prerequisite in this workflow.

Published/immutable releases, unexpected tag changes, extra old assets, partial
candidates and mismatched commits/builds are rejected. Replacement is a sequence
of API calls, not an atomic transaction: if interrupted after retagging or upload,
keep the draft unpublished, inspect the backup and run state, then restore or
complete it explicitly. Normal tag-triggered releases still refuse overwrites.

## Remaining release gates

- Ad-hoc signing provides local integrity; it does **not** establish an Apple
  Developer ID or notarization. Public downloads can still show Gatekeeper warnings.
  Add Developer ID signing/notarization later when the project has the necessary
  account, certificate and CI secret setup. No security settings are disabled.
- Native smoke is bounded boot/data/save/render coverage. It does not play through
  quests, test a real battle or prove audible output/controller behavior.
- Hosted Intel CI runs macOS 15, not the primary user's Monterey 12.7.5 machine.
  Keep Monterey launch, controls, audio and save/load as an explicit manual gate.
- Windows smoke runs on the hosted Windows Server 2022 x64 runner; it does not
  establish compatibility with every consumer Windows version or GPU. That runner
  has no audio device, so CI sets `ALSOFT_DRIVERS=null` for the test process only;
  [OpenAL Soft's backend override](https://github.com/kcat/openal-soft/blob/master/docs/env-vars.txt)
  allows startup without audible output. The distributed configuration is unchanged.
  Its system OpenGL driver reports only 1.1, below the engine's 2.0 minimum.
  `Tests/setup_windows_ci.ps1` downloads [Mesa 26.2.1](https://github.com/pal1000/mesa-dist-win/releases/tag/26.2.1),
  verifies its pinned SHA-256 and selects llvmpipe through the test process's
  environment. Mesa stays in the runner temporary directory and never enters
  player packages. The screenshot proves software rendering, not hardware GPU
  compatibility. Normal local smoke uses the machine's system graphics/audio.
  The unchanged Windows binaries have pinned hashes, but no verified matching source/build recipe
  is available in this repository. See `Runtime/Windows/PROVENANCE.md`.
- Linux smoke verifies the shipped launcher from outside the game directory on
  Ubuntu 22.04 and 24.04 using Xvfb, Mesa software rendering and null OpenAL audio.
  It checks all ELF dependencies with `ldd`, isolates HOME/XDG save paths and
  records boot/data/save/render results. Hardware audio/input, Wayland, other
  distributions and ARM Linux remain unverified.
- Runtime updates need an explicit provenance/hash review and all native platforms
  revalidated.

References: [GitHub runner architectures](https://docs.github.com/en/actions/reference/runners/github-hosted-runners),
[Apple nested code signing](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/Procedures/Procedures.html),
[GitHub draft/tag release options](https://cli.github.com/manual/gh_release_create).

## Release presentation

The release page has one player ZIP per OS: universal Mac, Windows x64 and Linux
x86_64. SHA256SUMS, build manifests, the editable project ZIP and the Markdown
notes file remain inside the verified CI candidate, not separate release assets.
GitHub also supplies its own source-code archives automatically.

Update the root RELEASE_NOTES.md for each version and follow
[the release-note template](../.github/RELEASE_NOTES_TEMPLATE.md). Notes are curated
for players as one flat changelog list. Do not split changes into sections or
append instructions to choose/download/unzip a platform or read a README. Include
only compatibility caveats that materially affect playing. Build logs, commit IDs, dependency details and test counts belong in
CI and contributor docs. The builder requires the note heading to match the
release version and uses this file as the GitHub release body.
