# DX and reliability review

Reviewed 26 September 2026 against `f1c0ce7b24744205920c665363c4edbfa81798f2`
(Demo 1 / 0.8.4). Scope: fresh-clone setup, Python generators, Ruby loading,
headless tests, save/quest boundaries, repository automation and release tooling.
No native graphical playthrough or exhaustive gameplay audit was performed.

## Assessment

The game has a stronger correctness foundation than its accumulated development
notes suggest. The pure Ruby domain model separates identity and spirit state
from engine integration. Tests exercise actual Essentials objects, save
roundtrips, item ownership, old-save migration, interrupted encounters and
full-bag retries. Authored maps have connectivity/softlock checks. Baseline
headless tests passed and all 177 recorded build-manifest hashes matched.

The main weakness is repeatability: too much depends on remembering generator
order, archived milestones and which test driver belongs to the current game.
Improve the build/test boundary before a broad gameplay refactor. Save class
names, quest keys, map/event IDs and the external save directory are compatibility
contracts and should remain stable.

## Findings and first-PR fixes

Severity: P1 means a risk of destructive build behavior or duplicate runtime
execution; P2 means a verification/reproducibility gap; P3 means maintenance cost.
These findings describe failure conditions, not evidence of corrupted current saves.

| Priority | Evidence at reviewed baseline | Consequence | First PR |
| --- | --- | --- | --- |
| P1 | `rebuild_scripts.py` checks `Plugins/Tidebound` only after writing Scripts, launch configuration, metadata and PBS; the check is an `assert` | A rejected rebuild still changes files; `python -O` skips the guard entirely, permitting two loading paths | Explicit preflight before writes; regression checks all affected outputs remain unchanged even under `-O` |
| P1 | `validate_maps.py` turns archive entries into a dict before counting custom scripts | Identically named duplicate entries disappear from validation, although the game executes both; load order is unchecked | Check original entry sequence, exactly one Main, exact source membership/order and contiguous placement before Main |
| P2 | Only the special `pond-recovery.yml` workflow exists; it targets a historical build branch and publishes releases | Normal PRs get no automated regression gate | Read-only `pull_request` / main verification workflow, Linux/macOS matrix, no publishing credentials |
| P2 | Python dependencies have no pinned install file; Whyduck generator uses `get_flattened_data()` | Full regional rebuild fails on Pillow 11.3.0 after earlier generators have already written data | Pin tested Pillow 12.3.0 and rubymarshal 1.2.10; document Python/Node versions and one setup recipe |
| P2 | `prepare_reference.py` writes into an existing directory; harnesses find scripts by numeric prefix | Renaming/reordering archive entries leaves stale candidates and may run the wrong reference source | Decode into staging and replace the extraction; regression covers stale filenames and decode failure |
| P2 | Map validation always writes `event_scripts.json`; manual test commands depend on a possibly stale report | Running checks mutates the checkout and Ruby compilation can target an old report | Explicit report-output option; verification passes a fresh temporary report to the native harness |
| P3 | Setup and present-day facts are interleaved with many superseded milestones | New contributors must reconstruct the current workflow | Add a current setup section and link it from the root README, test README and agent guide; preserve historical decisions |

Pillow introduced the required API in
[12.1.0](https://pillow.readthedocs.io/en/stable/releasenotes/12.1.0.html).
The pin is a tested build input, not a claim of byte-identical PNG output across
platforms.

## Remaining work, in recommended order

1. **Make rebuild/release operations transactional (P1/P2).** The preflight fix
   addresses the reproduced plugin failure, but generators still write multiple
   files in place. A later exception can leave a partial build. Stage outputs in
   a disposable checkout, run all gates, and promote only a complete validated
   result. `package_mac.py` currently packages whatever compiled files are present;
   add an explicit source-agreement gate and verify runtime-template hashes before
   a release. Retire the historical pond recovery publisher deliberately.
2. **Remove numeric engine-reference coupling (P2).** `native_domain.cjs` and
   `regional_snakes.cjs` select stock scripts by archive index, and some missing
   entries are silently skipped. Select stable names and fail if a required
   dependency is missing. Share the duplicated fixture loader. Test deliberate
   archive reordering before any Essentials upgrade.
3. **Broaden the automatic regression boundary (P2).** The default native-object
   harness covers opening/neighbour/hideout flows, but later features often rely
   on manually injected graphical drivers. Add pond victory/abort/loss, item retry
   and save migration to headless coverage. The map validator inspects only the
   first event page and recognizes selected literal transfer expressions; it is
   not an exhaustive event interpreter. Cover every authored page and explicit
   transfer command before introducing conditional multi-page content.
4. **Exercise rebuilds and packages in CI (P2).** The initial workflow checks the
   committed game, not full regeneration or packaging. Add a disposable rebuild
   job comparing Marshal data, source agreement and decoded pixels. Keep a native
   Intel Monterey launch/save/load/input/audio checklist as a separate release
   gate; macOS headless CI does not establish target-machine compatibility.
5. **Consolidate current state and reduce implicit build coupling (P3).**
   `AGENTS.md` is about 89 KB and includes obsolete version/map-count/platform
   statements. Split historical milestones from a concise current contributor
   guide without losing canon. Replace the map generator's shared-global `exec`
   chain incrementally with explicit inputs/outputs. Centralize duplicated release
   versions/build numbers after adding agreement checks. Avoid a wholesale rewrite.

## Verification evidence

- Baseline and fixed branch: 30 core/adapter tests pass; native-object opening,
  neighbour, hideout and regional-snake suites pass.
- Fixed branch: 11 build-tool regressions pass, including duplicate/archive order,
  stale source, plugin preflight under optimization, and reference replacement.
- All 16 maps / 275 events pass existing reachability checks; all 110 reachable
  maze resting positions can reach the goal; the pond island requires Surf.
- 25 custom Ruby scripts and 272 extracted event bodies compile in Ruby 3.2 WASM.
  The shipped engine uses Ruby 3.1; this is not a full engine compatibility test.
- Map regeneration reproduces all 16 binary maps. Generated PNG bytes differ
  between image-library environments, but the decoded map/art pixels match.
- Item, encounter and regional generators plus script rebuild pass with pinned
  dependencies in a disposable checkout. Compiled data, PBS and script archive
  match the baseline; sprite PNG compression differs.
- Local headless validation: macOS, Python 3.13.2, Node 24.14.1. The CI matrix
  uses Python 3.12 / Node 22; its remote results are separate from local evidence.

This change adds no game mechanic, balance, art, map, save-schema or release-version
change. Existing runtime binaries and compiled game assets are retained.
