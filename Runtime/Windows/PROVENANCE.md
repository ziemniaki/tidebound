# Existing Windows runtime

The Windows player ZIP reuses `Game.exe`, `x64-msvcrt-ruby310.dll` and
`zlib1.dll` from the original repository baseline
`f1c0ce7b24744205920c665363c4edbfa81798f2`. All three are x86-64 PE32+ images.
Their exact SHA-256 hashes are pinned in `release.json` and checked before
packaging. They are copied byte-for-byte; no engine upgrade, rebuild or new
publisher signature is introduced.

The existing Windows engine is mkxp-z with Ruby 3.1. The repository does not
provide a verified Windows source revision/build recipe corresponding to these
binaries; the pinned Mac source archive is not evidence of Windows provenance.
Replacing this runtime requires a separate provenance and native-test review.
Game/asset credits are retained in `CREDITS.md`.
