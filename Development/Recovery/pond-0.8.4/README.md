# Pond 0.8.4 recovery checkpoint — 26 September 2026

This is recovered source, NOT a released or currently rebuilt game. The game outside this folder remains verified 0.8.3. Do not merge this branch as a claim that the pond is playable. No new approval is needed to resume the already-authorized pond task.

## What happened

The pond was implemented, tested in a native Linux engine, locally committed as `1087636`, and packaged on 25 September. The GitHub blob upload was interrupted. The execution environment then disconnected and reverted to a much older 0.8.1 workspace snapshot. On 26 September the local commit, upload payload and new ZIPs were absent; GitHub main still correctly held 0.8.3 at `373239c79cb5a625a9d68264984b4046734f57e3` (tree `80769c40a09639945902e07853477d7ef6b874e6`).

These files were reconstructed from the visible successful authoring commands, including the final still-water, hidden-thicket and basket changes. Comments/formatting may differ. Do not claim byte-for-byte recovery of missing binaries, screenshots or ZIPs. They are reproducible from this source and the existing engine/assets.

The user explicitly asked to escape the retry loop while preserving progress. This checkpoint ends that recovery attempt. Do not automatically restart builds/upload loops in this turn.

## Retained design and implementation

- Expand map108 from56x68 to56x84, replacing only y48 onward. Keep all other map binaries unchanged.
- Irregular still-water pond, reeds, complete rocks, trees and small central islet. Separate compact TideboundPond atlas prevents changes to other locations and texture-limit problems. Preserve grass tile391.
- Existing level8 overworld Psyduck moves to19,62; keep `shoreduck_gone`, so an already captured/defeated one stays gone.
- PondGrass: Psyduck40% level8-11, regional Sunkern35% level8-10, Aipom25% level8-11. Only select it on map108 grass at y>=48. Northern road encounter table remains unchanged. Use existing regional hooks and native encounter selection.
- Three optional fishermen: Toma at25,55 (Magikarp9/Goldeen10), Ida38,63 (Wooper10/Poliwag11), Renzo29,72 (Barboach12). Existing astral battle-loss adapter; only victory records completion.
- Oran tree20,54: existing two-berry/regrowth behavior.
- Hidden western thicket route ends13,69: one-time Mystic Water, full-bag retry supported.
- Obelisk27,61: future Surf access only. StillWater terrain; Surf passability only for surfing player, not NPCs. No new HM, badge, quest gate, inscription explanation or mythology.
- Once-only migration moves old saves on new obstacles/water/islet to26,52. Map magic26092503. Mac0.8.4/build38, existing save identity/font fix/runtime.

## Resume once, from this checkpoint

1. Confirm current GitHub main and preserve unrelated changes. Use a feature branch/worktree based on0.8.3 plus this checkpoint. Do not resume from the old scratch snapshot.
2. Run `python Development/Recovery/pond-0.8.4/restore_source.py`. It checks exact baseline patterns before editing, copies source/tests and applies all small integration changes. If a check fails, inspect that difference; do not blindly rerun it.
3. With rubymarshal1.2.10/Pillow installed, run sequentially with failure stopping the chain:
   - `python Development/rebuild_maps.py`
   - `python Development/rebuild_field_data.py`
   - `python Development/rebuild_scripts.py`
   - `python Development/validate_maps.py`
   - `python Development/Tests/pond_geometry.py`
4. The map builder generates024_PondGeometry.rb, pond_manifest.json, the private atlas, compiled maps/masks and preview. Check the other15 map binaries against0.8.3.
5. For native validation, inject Tests/pond_native.rb before Main into a DISPOSABLE Linux engine copy only. Existing runtime was mkxp-z826929e. Prior launch worked with DISPLAY=localhost:91, ALSOFT_DRIVERS=null, LIBGL_ALWAYS_SOFTWARE=1 and LD_LIBRARY_PATH=./lib64. Do not reuse stale PASS files. Never embed the test driver in release Scripts. TB_POND_VISUAL=1 renders screenshots without battles.
6. Update Bible1.30 with section32, Guide2.29, README/START_HERE/MAC_README/PROJECT_STATUS and validation record. Update render_bible.py's two hardcoded version labels as well as the Markdown header; regenerate/inspect PDF. Recompute BUILD_MANIFEST hashes after final changes.
7. Commit/push SOURCE and verify remote tree BEFORE packaging large artifacts. Then package_mac.py into a fresh0.8.4 output folder, make the editable project ZIP from the exact commit, and verify ZIP integrity/game-file equality, plist version0.8.4/build38 and executable permissions. No macOS execution is available here; do not claim a Mac playtest.
8. Publish/download only verified artifacts. A timeout/offline error gets one bounded check, then an explicit checkpoint; do not repeatedly upload from an unstable workspace.

## Bible section32 content to retain

The southern coast road opens onto an inhabited pond, with the relocated Psyduck and Psyduck/Aipom/Sunkern grass. Optional fishermen, a healing berry tree and a concealed path reward exploration. A stone obelisk on an island is reserved for later Surf. Toma, Ida and Renzo are provisional implementation names; their dialogue is about everyday fishing, nets, bait stolen by Aipom and tending the tree. They do not explain the obelisk. Its origin, inscription, purpose and any later reward remain open. Existing regional Psyduck/Sunkern definitions are unchanged. Also record the approved0.8.3 colder squat presentation without changing its quest.

## Historical validation (not a new run)

Before the reset, validate_maps passed275 events with959 connected road walking cells; the island was explicitly excluded from foot-only event reachability and separately tested. The pond geometry test proved all actors/rewards and the full hidden path reachable, the islet isolated on foot and reachable with Surf. Native Linux checks passed300 pond selections, northern table preservation, duck relocation, terrain/Surf/NPC restrictions, old-save relocation, one-time item collection, a real fisherman battle, persistent victory and native save. Final still-water/thicket presentation and Bible PDF were visually inspected. The last basket addition was included in the offline overview.

The missing Mac ZIP had SHA256 `7da9a47bd9fa5da6a640b2b691eba45cd9b6dbd8fdcbd60a8bfd8684b06e282b`. This is historical provenance only: a new ZIP may differ due timestamps. There is no valid0.8.4 download link until rebuilt or recovered and verified.
