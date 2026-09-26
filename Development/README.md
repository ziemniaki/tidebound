# Editing this prototype

## Fresh-clone setup and checks

Use Python 3.12 or 3.13 and Node.js 22 or 24. From the repository root on
macOS/Linux (select your installed Python version when creating the environment):

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
npm ci --prefix Development/Tests --ignore-scripts
.venv/bin/python Development/verify.py
```

On Windows, use `py -3.12 -m venv .venv` and replace `.venv/bin/python` with
`.venv\Scripts\python.exe`. Python and Node are development tools only.
The pinned Pillow version supports the sprite generators' `get_flattened_data`
API. Optional audio regeneration separately needs NumPy/ffmpeg; bible PDF
regeneration needs ReportLab and the fonts named in `render_bible.py`.

`verify.py` runs build-tool regressions, map/source agreement, maze and pond
geometry, core/adapter tests, native-object quest/save tests and regional-snake
tests. It refreshes ignored engine references and extracts current event scripts
to a temporary file; it does not rebuild or rewrite tracked game files. Run
without Python `-O` or `PYTHONOPTIMIZE`. PR CI uses the same command on Linux and
macOS. This is headless coverage, not a Monterey or Windows graphical playtest.

`validate_maps.py` is read-only by default. To deliberately refresh the tracked
event report after a map edit, run:

```sh
.venv/bin/python Development/validate_maps.py --event-scripts Development/event_scripts.json
```

## Source and rebuild ownership

For isolated regeneration, universal Intel/Apple Silicon Mac packages, native
smoke checks and tag-driven draft releases, use [RELEASING.md](RELEASING.md).
`release.json` owns package metadata and pinned runtime input hashes. Mac builds
now require macOS signing tools; historical Linux/standard-library-only packaging
instructions below describe the old unsigned packager.

The numbered Ruby files are the authoritative custom source. They are already
embedded in `../Data/Scripts.rxdata`, immediately before Main. Do not also copy
them into Plugins: that would load them twice.

After editing a numbered file, run `python rebuild_scripts.py` from this folder.
It replaces only the Tidebound script entries and applies the documented title,
version and project metadata settings. Back up any separate custom changes to
those settings before rebuilding.

The project can be opened through `../Game.rxproj` with RPG Maker XP. Generated
maps have IDs 101–116. Their collision masks live in `003_MapPassages.rb`.
**If you change map geometry in the editor, update those masks too.** The map
validator checks generated connections; it is not a live graphical playtest.

`rebuild_maps.py` regenerates all sixteen opening maps from their declarative
layouts, and overwrites edits made to those sixteen maps in the editor. It leaves
the stock demo maps intact. It also sets the opening start position.

Build prerequisites are pinned in `requirements-dev.txt`. The optional audio
script also requires NumPy and ffmpeg. The game itself does not need Python.

Typical source workflow:

```
python rebuild_maps.py
python rebuild_opening_items.py
python rebuild_neighbor_data.py
python rebuild_field_data.py
python rebuild_regional_data.py
python rebuild_scripts.py
python validate_maps.py --event-scripts event_scripts.json
```

Run this sequence from `Development/` with the virtual environment active.
Only rebuild maps when intentionally changing generated geometry; numbered Ruby
changes need `rebuild_scripts.py` and verification, not a full map rebuild.
Review generated diffs before committing. PNG compression can vary between
platforms/library versions even when decoded pixels match. Generators still
write multiple files in place; use a clean branch or disposable checkout when
testing a full rebuild. See [the DX/reliability review](DX_RELIABILITY_REVIEW.md)
for the remaining follow-up work.

`Tests` contains the Ruby mechanic suite and the headless native-object smoke
harness. Read its README for their scope and execution instructions.

`design_bible.md` retains the full story direction and late-game plans. The
current opening deliberately contains none of those late-game reveals.

Known balancing choices are provisional: quarter-HP rest/recovery, six turns
and catch-rate 35 for spirits, 18 Poké Balls on each astral arrival, a temporary
guide Natu, and a new Natu if everybody is lost. Saving is manual. A separate
player-body HP system and enforced autosave have not been implemented.

Native-save compatibility fix in 0.2: Essentials' `ensure_class` expects a
simple symbol constant. `TideboundSaveState` aliases `Tidebound::State` so the
engine can validate and serialize this state correctly.

Opening 0.4 adds the bedroom, family scene, native Pookie follower, optional pier
run, 100-step return, post-walk choice and forest keys. 006_FirstWalk.rb owns
these new scenes and quest hooks. Existing 0.2/0.3 saves migrate additively.
Tests/opening_flow.rb covers the sequence and saves; rendered_smoke.rb is a
TEST-ONLY injection for a disposable engine copy, never a release script.
The Mac config's fontHeightReporting must remain 1 to prevent clipped letters.

Use `python Development/build_release.py /path/to/new-output-folder` on macOS
from a clean project root for verified candidates. Read RELEASING.md and
Runtime/macOS/PROVENANCE.md.

Coast 0.5: 007_Coast.rb adds layout helpers, save translation and gentle camera
staging. Map 102 uses a (24,20) offset inside CoastMap. Event and checkpoint
coordinates in the engine remain native. Use travel_coast for local coast anchors.
The map is 108x88; leave ocean beyond every reachable camera viewport.
Retain the first eleven coast event IDs and use the current map magic 26091006.

Night 0.5.1 is a palette/lighting correction. 004_Opening.rb owns the fixed
outdoor tone and story-map night policy. Daylight exceptions require explicit
approval and an entry in DAYLIGHT_MAPS (currently empty). Do not enable automatic
TIME_SHADING. Map geometry and coastal revision 5 remain unchanged.

Neighbour quest 0.6: 008_NeighborQuest.rb owns the additive quest state, dialogue,
NPC trainer rosters and event methods. 009_NeighborPresentation.rb draws small
household props. New maps 108/109 are a short coastal pursuit and local storehouse.
rebuild_neighbor_data.py maintains the new Key Items/types and their PBS files.
The trainer! adapter uses the same astral loss handler as wild!, including its
pre-heal snapshot. Old completed-oil saves can collect a belated pie.

Tests/neighbor_flow.rb adds saved stage transitions, loss/draw/retry, all three
starters and full-bag handoffs. Tests/rendered_neighbor.rb is a disposable native
test driver, never release code. Its setup script takes a matching Linux engine
directory and an output directory outside this project. See Tests/README.md.

0.6.1: 010_FieldDetails.rb and rebuild_field_data.py own field resources, grass
encounters, timed fire recovery and local presentation. Fire healing now grants
full HP/PP per 15-minute cooldown; astral recovery retains the old floor.

Dock refinement 0.7.1: dock_details.py extends map 112 at the end of vault_maps.py.
013_DockDetails.rb owns exact glass-pixel illumination, dock props and additive
safe-position migration. Opening.animate preserves actor through state after
native move routes. Hidden cutscene actors must remain through. Current map
magic is 26091201; schema/coastal translation are unchanged. See
validation_docks.md for actual doorway movement and window-mask checks.

Regional form 0.7.2: run python3 Development/rebuild_regional_data.py before
rebuild_scripts.py to regenerate SUNKERN_1 and its PBS definition. Runtime
encounter selection is in 014_RegionalForms.rb. Art source and export command
are in Art/Sunkern. Map data and existing Pokemon are not migrated.

Moonkern 0.7.3 extends rebuild_regional_data.py with a new species and metrics.
Run it before rebuild_scripts.py. Evolution is native Level 24 on SUNKERN_1;
MOONKERN declares DefaultForm_0. The obsolete regional Sunflora setter was
removed. Art and mechanical export are in Art/Moonkern.

0.7.4: rebuild_regional_data.py invokes rebuild_moonflora_data.py for Moonflora
and the 14/20 evolution chain. Art/Moonflora/export.sh exports the simplified
sprite. Regenerate data before rebuilding scripts and packaging.


0.7.5: rebuild_regional_data.py also invokes rebuild_wurmple_data.py. The latter
maintains WURMPLE_1 and its separate PBS form file. Run Art/Wurmple/recolour.py
for the authorized exact palette edit, then rebuild_scripts.py before packaging.
014_RegionalForms.rb selects the form in forest 103; evolution designs are deferred.


0.7.6: rebuild_regional_data.py -> rebuild_wurmple_data.py ->
rebuild_glaciverm_data.py now authors the native level-10 split. Glaciverm is
complete; Frostcoon is a provisional white Bug/Ice cocoon. Its planned level-55
dragon is not implemented. Art/Glaciverm/export.sh builds sprites from the
retained atlas. Tests/rendered_glaciverm.rb supersedes the older Wurmple test.


0.7.8: Art/Lapras/edit_sprites.py edits the retained stock assets directly.
rebuild_lapras_data.py maintains LAPRAS_1 and its independent PBS suffix;
rebuild_regional_data.py invokes it. Rebuild scripts after data. The existing
pier sprite selects the new form; no map generator or encounter changes.


0.7.9: mouth_detail.py adds yellow Wurmple-like eyes and a deeper omega-shaped
snout notch. icon_detail.py restores the yellow eye rim after icon reduction.
Run Art/Glaciverm/export.sh (from Development) to reproduce the complete edit.
Rear sprite, body and gameplay data remain unchanged.


Historical 0.7.10 (moves superseded below): Frostcoon is now an authored Bug/Ice cocoon with blue frozen-silk sprites,
a yellow eye, BST 350, Shell Armor and a complete level-up moveset through 54.
The level-55 Ice/Dragon remains future content. Existing Frostcoon keep their
identity, moves, HP and status while cached stats/old Shed Skin update on load.

Run rebuild_glaciverm_data.py for this species update; rebuild_regional_data.py
also reaches it via rebuild_wurmple_data.py. The former invokes the maintained
manual palette recipe in Art/Frostcoon. Rebuild scripts to embed 015_Frostcoon.rb.
No map regeneration is needed. See validation_frostcoon.md.


0.7.11: Frostcoon now learns only status moves: hazards, HP support, weather,
sleep/paralysis and protection. Stats, Shell Armor, art and evolution are unchanged.
Existing attacks are replaced on load or when Wurmple evolves; selected support
moves and their PP remain. Replacement PP never exceeds the old slot's PP.
Wish heals a teammate switched into its place; Life Dew heals active allies.
Neither cures poison. See Art/Frostcoon/species_sheet.md under Development.


### Historical Ice/Dragon final-evolution sprite milestone - 16 September 2026

Approved butterfly-dragon front artwork, matching rear view and two-frame party
icon are now installed as FROSTCOON_EVOLUTION (art identifier only). The original
approved design, rear source, reproducible export script and previews live in
Development/Art/FrostcoonEvolution. Battle canvases are 160x160; icon 128x64;
shared 16-colour palette, binary alpha and same-palette provisional shiny assets.
Gameplay remains 0.7.11. Name, species data, cry, final metrics and the playable
level-55 evolution remain pending; Frostcoon itself is unchanged. Do not invent
those decisions merely because sprite assets now exist.


0.7.12: Nivalora (working name) completes Frostcoon's level-55 evolution.
Ice/Dragon, 600 BST, fast special attacker, Shield Dust, gentle sleep/HP support.
Approved front and corrected rear sprites, icon and provisional same-palette
shiny art are active. See Development/Art/FrostcoonEvolution/species_sheet.md.
Existing Frostcoon evolve at their next qualifying level-up; saves retain their
companions. No new wild encounter or story event. Articuno cry is provisional.


0.7.13 evolution-testing build: a NEW GAME starts with 99 Rare Candies in the
bag. This supply is granted once in begin_story; continuing an existing save
does not grant or refill candies. Nivalora and all previous content are retained.


Landscape 0.7.14: `landscape.py` is the outdoor pass in rebuild_maps.py. It composes
native nature art, water depth palettes and collision masks. Do not edit the
generated TideboundLandscape atlas directly. Rebuild maps, then scripts, then
run validate_maps.py. 016_Landscape.rb provides additive old-position recovery.
Native visual fixture: Tests/rendered_landscape.rb (test-only injection).

0.7.15: grove clearings and scree regions are authored in landscape.py. Keep
protected scripted corridors intact. Threshold cue placement lives in
010_FieldDetails.rb; save recovery is now landscape revision 2.


0.7.16: lighthouse_interiors.py runs after landscape.py. It owns maps
101/104/107/110/111 furniture, floors, walls, windows, beacon and full stairs.
017_Lighthouse.rb adds the existing lamp flag's lens glow. Native integration
fixture: Tests/rendered_interiors.rb. Inject tests into a disposable runtime,
never release Data/Scripts.rxdata. See validation_interiors.md for evidence.


0.7.17: psychic_maze.py owns map 114 and generates coordinate constants in
018_PsychicMaze.rb. Edit its Python geometry, rebuild maps/scripts, then run
validate_maps.py and Tests/maze_graph.py. Native fixture: rendered_maze.rb.
Preserve off-trigger warp landings and new-game-only state.

The false bedroom (115) is generated by dream_room.py after psychic_maze.py. Its state and dialogue are in 019_DreamRoom.rb; test with Tests/rendered_dream.rb in a disposable engine.

Map 116 is generated by folded_room.py after dream_room.py; both use 019_DreamRoom.rb. Regenerate maps then scripts. The four-riddle room never changes the existing 114 maze.

020_BirdPrelude.rb adds a self-contained New Game scene before the existing map115 autorun. It changes no maps. Rebuild scripts after editing its graph, timings or visuals; test with rendered_bird_prelude.rb in a disposable engine.

0.7.22: To rebuild the new Water/Psychic shore Psyduck and Whyduck after other regional species, run `PYTHONPATH=build_tools python3 Development/rebuild_whyduck_data.py`; it also runs `Development/Art/Whyduck/draw_sprites.py`. `rebuild_regional_data.py` invokes it automatically. Run `rebuild_field_data.py` for the road encounter, then `rebuild_scripts.py` for the wild-form event.

0.7.23: Whyduck's 2x pixel-grid artwork was fully redrawn from the supplied visual direction. Run Development/Art/Whyduck/draw_sprites.py to regenerate five native sprites; rebuild_whyduck_data.py also runs it. Sprite metrics changed to front 1,13 / back 0,5. No gameplay species fields changed.

0.7.24: Approved Whyduck artwork: a pink brain, original Psyduck eye, hand and bill pixels, down-left gaze and a mirrored casting pose. Other gameplay is unchanged.


## Demo 1 / 0.8.0 — 23 September 2026

The opening caption now adds “Take it for a little walk, 100 steps.” This is wording only: guide Natu to the bed as before; no step counter was added. Pokémon losing their HP are described as having died, including field poison, while the existing battle and astral mechanics are retained.

Shiohama's three cottages use salt-weathered dark timber and stone footings. Window glass and its warm light stay aligned. The lighthouse artwork is unchanged. South Coast Road has a visible level-8 Tidebound Psyduck near the shallows, in addition to its existing rare grass encounter. Regional Psyduck now evolves into Whyduck at level 16; an older regional duck above 16 evolves at its next level-up. Ordinary Psyduck still evolves into Golduck at 33.

The docks now have two wooden sailing ships, sixteen new sailors including a captain, cargo stacks, a sailing notice, a ledger and a modest memorial. Nell (Wingull 8, Wooper 9) and Oren (Poliwag 10, Krabby 11) offer optional battles and remember a win. These use the existing astral-loss flow; neither is required for the story. Other sailors discuss trade, letters, watches, mountain settlements and everyday coastal life without explaining the late mythology.

Speak to the captain at the end of the eastern pier about **Psyduck Island**. Accepting reaches the demo's ending message. You remain in the docks and can continue exploring and saving. The island and voyage gameplay are future content.

Continue preserves existing party, inventory and quest flags. Updated map data reloads on old saves; a player standing where a new dock actor was placed is moved to a nearby clear tile. New Game is required to see the opening caption. The previous 99 starting Rare Candies remain available for evolution testing; this release does not remove user-requested supplies. Keep a backup before overwriting a save with a new journey.

Build additions: demo_maps.py / demo_art.py / 022_DemoLaunch.rb; run rebuild_whyduck_data.py for the level16 evolution. See AGENTS.md and validation_demo_080.md.


0.8.2: hideout_room.py regenerates map109 through lighthouse_interiors.py. 023_Hideout.rb owns the guarded sofa, isolated rune-console minigame and boss/cache handoff. Rebuild maps/scripts and run validate_maps.py plus Tests/native_domain.cjs. Tests/hideout_native.rb is a disposable graphical driver; keep it outside release Scripts. See validation_hideout.md.

## 0.8.3 — neglected squat atmosphere

hideout_room.py replaces map109's domestic furnishings with code-drawn pallet mattresses, broken crates/locker, torn sofa, battered wash trough and improvised bench. Windows are boarded; no household lamp or neat rug remains. Floorboards and limewash are damp and cracked. The final palette pass clones tiles instead of recolouring shared entries, protecting every lighthouse room. 004_Opening.rb gives map109 a dedicated Tone(-35,-32,-25,95). Collision masks and event positions are unchanged. Map magic26092502 refreshes existing saves. Mac build37. Native screenshots and focused validation are in HideoutEvidence_083 and validation_hideout_atmosphere.md. No new lore or quest changes.

## 0.8.4 — southern pond, 26 September 2026

Map108 now has a substantial pond clearing. The existing level8 Psyduck moves to19,62 and retains shoreduck_gone. Local pond grass: Psyduck40% level8-11, regional Sunkern35% level8-10, Aipom25% level8-11. Northern road encounters are unchanged. Three optional fishermen remember victories and use the existing astral-loss adapter: Toma (Magikarp9/Goldeen10), Ida (Wooper10/Poliwag11), Renzo (Barboach12). An Oran tree uses existing two-berry regrowth. The hidden western path ends in a one-time Mystic Water with full-bag retry.

The central obelisk requires later Surf. Pond water has StillWater terrain and player-only Surf passage; no HM or badge is awarded. Its origin, inscription, purpose and future reward remain open. Older saves on new obstacles/water/islet move once to26,52. Map magic26092503; Mac0.8.4/build38; same runtime, font fix and save identity.

pond_map.py runs after demo_maps.py and generates024_PondGeometry.rb plus a compact road-only atlas. 025_Pond.rb handles pond encounters, optional battles, item and migration. Grass tile391 is preserved. Tests/pond_geometry.py verifies the island is unreachable on foot and reachable with Surf; validate_maps.py explicitly excludes the future-Surf obelisk. All other15 maps remain unchanged. The recovery recipe is now historical; do not apply it again. See Development/validation_pond.md.
