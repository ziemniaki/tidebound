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

## Independent feature work

Use separate checkouts for simultaneous agents. A branch change in a shared
working directory does not isolate edits or builds. Before splitting a feature,
identify its source owner and shared contracts: map/species/form IDs, actor names,
handler keys, public Ruby calls and source load order. Agree only those touched
by the work; no ticket or registration service is required.

Keep an area/feature's source edits together. Coordinate changes to
`src/load_order.txt`, `maps/compiler.py`, `maps/registry.py`, species catalogs and
shared NPC dispatch; these are integration points rather than free-for-all files.
The [root task table](../AGENTS.md#read-for-your-change) routes to scoped workflows.

Each branch should include source and its generated outputs for review. When
combining changes, resolve source first, then regenerate once from the combined
source. Do not merge binary script/data archives by choosing one branch's copy:
that can silently discard the other feature. Preserve stock engine inputs and
reconcile supplied editor changes before rebuilding. Never regenerate over
another agent's active checkout.

For generated-data conflicts, use a known common baseline for the generated files,
apply the combined source, run `uv run format` and `uv run rebuild --all`, then
stage new sources/outputs and run `uv run check --all`. Choose that baseline only
for files confirmed generator-owned; stock data and direct asset/editor edits
need their own reconciliation. New script entries must be in the combined manifest.

Changes to workflow definitions need branch-dispatched verification to exercise
the new workflow; ordinary `/verify` runs the trusted workflow. Docs-only PRs
need link/contract review and quick checks, not full player builds. Do not widen
the status-writing job's permissions to execute untrusted PR code.

When handing off, report the branch/commit, current checks and remaining work.
Do not claim a push, release or playtest happened without verifying it. Accepted
creative decisions belong in `specs/`; working instructions belong in `docs/`.
