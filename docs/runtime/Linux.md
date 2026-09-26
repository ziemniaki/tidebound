# Linux runtime provenance

- Upstream: https://github.com/mkxp-z/mkxp-z
- Commit: `826929eeb3ebc4b887c011604919217a790770f4` (same source as the Mac runtime).
- Build: https://github.com/mkxp-z/mkxp-z/actions/runs/28475006907
- Artifact: `7993780545`, `mkxp-z.linux.ubuntu.22.04.x86_64.dev-826929e`.
- `mkxp-z-826929e-ubuntu22.04-x86_64.zip` is the unchanged GitHub artifact ZIP.
- SHA-256: `9feba61c70aa63e98ca87678002dc6eb4cbda2fca09c2e1a63122fd332979053`.

The executable and the three bundled ELF libraries are x86_64. The executable
and Ruby reference GLIBC_2.35, making Ubuntu 22.04/glibc 2.35 the initial baseline.
The executable's RUNPATH includes `$ORIGIN/lib64`; the upstream build-directory
entry is retained. We do not patch or rebuild the native binaries.

Packaging retains the executable, lib64, stdlib and license; it replaces the
upstream example game/configuration with the project's verified game files.
The ZIP artifact did not retain executable bits, so the player packager sets
0755 on the engine and the new launch script. That script sets the game working
directory and invokes the bundled engine without changing global library paths.

Engine source is pinned at
`runtime/macOS/mkxp-z-826929e-portable1-source.tar.gz` (SHA-256
`f21396819b9479ad7b33f061702f0e5e9c46f49edb4cc37f17842d3c11320708`).
It is included in the Linux player ZIP, together with upstream's license.
This source snapshot includes Tidebound's portable Mac path patch; that patch
changes only the macOS implementation. The Linux binary remains the unchanged
upstream artifact identified above.
The source's `linux/Makefile`, `linux/vars.sh` and `.github/workflows/autobuild.yml`
record the upstream dependency/build recipe. Dependency source projects and
their licenses remain governed by their upstream terms.

System libraries are required; this is not an AppImage or a static binary.
See docs/players/linux.txt for the tested Ubuntu package names. Runtime updates must
review the artifact hash, matching source and system requirements together.
