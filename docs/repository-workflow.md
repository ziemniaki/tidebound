# Repository workflow

`ziemniaki/tidebound` is authoritative. Start from the current checkout and
preserve uncommitted changes; release ZIPs are distribution snapshots.

1. Read `AGENTS.md`, [current status](status.md), and the relevant code/specification.
2. Make a focused branch in the original repository. Preserve saves, canon and art.
3. Keep source and generated game files synchronized. Use `uv run play` locally
   and `uv run check` before review; generator changes also need `check --all`.
4. Open a PR explaining the resulting behavior and actual verification. Request
   full platform verification with `/verify` before merging substantial work.
5. Update current documentation where behavior changes. Keep saves, credentials,
   caches and generated distribution ZIPs out of Git.

Quick checks run on pushes. Full builds are on demand and on release tags.
See [releasing](releasing.md) for exact-head review and publication. A tag creates
a draft; it does not publish automatically. Release pages contain three player
ZIPs; technical metadata and the editable project archive remain CI artifacts.

For this directory migration, the old workflow on main still refers to the old
layout. Dispatch Full verification on the PR branch to test the new definitions
before merging; subsequent `/verify` requests use the updated trusted workflow.
Do not change the authorization boundary to execute untrusted PR code in a
status-writing job merely to handle a path transition.

When handing off, report the branch/commit, current checks and remaining work.
Do not claim a push, release or playtest happened without verifying it. Accepted
creative decisions belong in `specs/`; working instructions belong in `docs/`.
