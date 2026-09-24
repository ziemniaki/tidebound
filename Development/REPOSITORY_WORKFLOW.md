# Repository workflow

## Source of truth

Use the public `ziemniaki/tidebound` repository as the authoritative working project (initial import verified on 24 September 2026). Begin each task from its latest branch, not an old ZIP or chat memory. The public repository includes full story spoilers in the design bible.

The initial import contains Demo 1 / 0.8.0 only. It starts a new Git history; no previous game versions are imported. Keep all subsequent development changes in normal commits so work can be reviewed and recovered. Current maintenance tests and source art are part of this snapshot even when their filenames reference the feature version that introduced them.

## Working rules

1. Read AGENTS.md, PROJECT_STATUS.md, and the relevant code/bible sections.
2. Create a focused branch for changes. Preserve player saves, canon, current art and working systems.
3. Keep numbered Ruby sources, compiled Scripts.rxdata, PBS/compiled data, map masks and generated assets synchronized when applicable.
4. Verify the actual changed behavior. Update the current status and relevant bible/guide sections in the same change.
5. Keep saves, credentials, local caches and generated distribution ZIPs out of Git.
6. Commit work and report the branch/commit. Do not claim GitHub is up to date until the push and remote content have been verified.
7. Put playable builds and the editable project ZIP in GitHub Releases. Do not commit large distribution archives into the source tree.

The saved Library 0.8.0 downloads remain a recovery copy; ongoing repository-backed items should not also be maintained as a second competing Library codebase. If remote access is unavailable, state the last verified commit and the unsynced changes explicitly.

## First-import mechanism

The one-time import workflow downloads the exact checked release asset, verifies its SHA-256, and imports its single project directory. Its GitHub token is scoped to writing repository contents during that job. It does not run game scripts. The import succeeded and removed its own workflow; no ongoing write automation remains. Verified import commit: `19780315bf4227f24ab9b5ccdf6d8ee54b6e773e`.

Release v0.8.0 was created before source import, so its automatic Source code archives contain the initial documentation snapshot. Use the named `Tidebound_Project.zip` release asset or clone `main` for the full game. Future release tags must point to the verified complete source commit.
