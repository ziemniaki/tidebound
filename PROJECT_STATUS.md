# Current project status

Demo 1 / 0.8.5 · Bible 1.30 · Guide 2.30 · 26 September 2026

## Mac ZIP extraction fix — after 0.8.5

A browser-downloaded 0.8.5 ZIP matched its release checksum, but Archive Utility
changed the Unicode spelling of `Routé 1.mid`, invalidating the app's sealed
resource signature. Python/ditto extraction preserved that spelling, so earlier
CI and local checks missed the failure. Packaging now normalizes bundle filenames
to NFD before signing and repeats that normalization during ZIP verification.
Game files retain their bytes; no saves, gameplay or runtime code change.
Developer ID signing/notarization remain separate, unresolved distribution work.
The existing 0.8.5 tag and release assets are not replaced by this source fix.
Validation: 30 tooling tests pass; a rebuilt universal preview retains a valid
strict signature for both architectures after extraction with the actual macOS
Archive Utility. Native ARM boot/data/save/render smoke also passes on the local
Apple Silicon Mac. This verifies extraction integrity, not notarization approval.

## 0.8.5 — release preparation

Version0.8.5 / Mac build39 packages the verified build-workflow changes from
PR #2. Deliverables are the universal Mac player ZIP, Windows x64 player ZIP,
editable project, provenance manifests and checksums. This is a packaging release:
gameplay, maps, assets and save identity are unchanged from 0.8.4. Only the embedded
Settings and Tidebound version constants change in the game script archive.

The version update must pass CI before it is merged and tagged. The tag workflow
then reruns the gates and prepares an unpublished draft; inspect GitHub Releases
for the current publication status. Full gameplay, audio/controller behavior and
Monterey target-machine checks remain manual. The evidence below records the
preceding tooling work; its historical version and publication statements are not
claims about the 0.8.5 release.

## Windows player packaging — development branch

The release candidate now includes a dedicated Windows x64 player ZIP. Its
executable and DLLs are unchanged and pinned by hash; staging verifies x64 PE
headers, copied files, and ZIP extraction. The package excludes development/editor
files and includes launch instructions, credits and provenance. A Windows Server
2022 CI job verifies downloaded checksums and runs the shared native boot/data/save/
render fixture with an isolated save directory. Hosted Windows results are recorded
in [PR #2 checks](https://github.com/ziemniaki/tidebound/pull/2/checks); the prior Mac
evidence below remains separate.
No game data, save namespace or runtime binaries are changed.

## Universal Mac builds and release workflow — development branch

`release.json` pins package metadata and runtime hashes. Packaging now stages a
universal Intel/Apple Silicon app on macOS, signs it ad hoc, verifies both native
architectures/dependencies, checks all game files, and verifies the ZIP roundtrip
before exposing output. `build_release.py` requires a clean commit and adds the
editable project, source manifest and checksums. `check_rebuild.py` regenerates
assets in isolation and compares binary data and decoded PNG pixels.

The reusable CI workflow prepares artifacts and requires native ARM/Intel smoke
tests. Matching version tags on main's history prepare draft GitHub releases;
the pond-specific publisher is retired. Hosted verification, regeneration,
universal packaging and native smoke on ARM macOS 14 / Intel macOS 15 passed
in [run 36245127653](https://github.com/ziemniaki/tidebound/actions/runs/36245127653)
(commit `a14f1b9`). Tag-driven draft publication remains unexercised; no release
or tag was created or replaced.

Local evidence: 22 build-tool regressions and all existing headless suites pass;
isolated regeneration matches. The universal Mac preview passes signing and
archive checks. Its native ARM smoke passes on an Apple M1 Pro / macOS 26.1 with
Ruby 3.1.3 and Metal, including compiled data, actual Pokemon/state disk save
roundtrip and font rendering. Hosted Intel native smoke also passes. Full gameplay
and Monterey 12.7.5 controls/audio/save testing remain separate gates. See RELEASING.md under
Development for the commands and exact scope. Runtime code and game version remain
unchanged; signatures and package layout are updated.

## Development tooling review — 26 September 2026

The DX/reliability branch adds pinned Python development dependencies, a single
headless verification command and read-only PR CI on Linux/macOS. The script
rebuilder now rejects duplicate plugin installation before writes; archive
validation detects duplicate, stale or misplaced custom scripts; reference
extraction removes stale numeric filenames. Map validation no longer rewrites
the tracked event report by default.

Local checks pass: 11 tooling regressions, 30 core/adapter tests, native-object
quest/save and regional-snake suites, all 16 maps, maze and pond geometry, and
compilation of 25 custom scripts / 272 event bodies. These are automated headless
checks, not a new native graphical or Monterey playtest. Gameplay, saves, release
version and compiled game data are unchanged. See
`Development/DX_RELIABILITY_REVIEW.md` for evidence and remaining priorities.

## 0.8.4 — southern pond, 26 September 2026

Map108 now has a substantial pond clearing. The existing level8 Psyduck moves to19,62 and retains shoreduck_gone. Local pond grass: Psyduck40% level8-11, regional Sunkern35% level8-10, Aipom25% level8-11. Northern road encounters are unchanged. Three optional fishermen remember victories and use the existing astral-loss adapter: Toma (Magikarp9/Goldeen10), Ida (Wooper10/Poliwag11), Renzo (Barboach12). An Oran tree uses existing two-berry regrowth. The hidden western path ends in a one-time Mystic Water with full-bag retry.

The central obelisk requires later Surf. Pond water has StillWater terrain and player-only Surf passage; no HM or badge is awarded. Its origin, inscription, purpose and future reward remain open. Older saves on new obstacles/water/islet move once to26,52. Map magic26092503; Mac0.8.4/build38; same runtime, font fix and save identity.

pond_map.py runs after demo_maps.py and generates024_PondGeometry.rb plus a compact road-only atlas. 025_Pond.rb handles pond encounters, optional battles, item and migration. Grass tile391 is preserved. Tests/pond_geometry.py verifies the island is unreachable on foot and reachable with Surf; validate_maps.py explicitly excludes the future-Surf obelisk. All other15 maps remain unchanged. The recovery recipe is now historical; do not apply it again. See Development/validation_pond.md.

## Demo 1 / 0.8.3 — squat atmosphere

Map109 is now cold, pale and neglected: boarded windows, peeling walls, damp floorboards, torn pallet mattresses, battered sofa, broken crates and an open locker. Warm lamps, neat rugs and domestic shelving are removed. All collision masks, event positions and quest mechanics are preserved. Art uses private cloned atlas tiles; the lighthouse keeps its original appearance. Map magic26092502 refreshes old map caches. Mac build37, same runtime and save directory. See Development/validation_hideout_atmosphere.md. GitHub release publication is pending; last verified published release is 0.8.1.

## Demo 1 / 0.8.2 — 25 September 2026

Map109 is now the youths' untidy home and a short clutter maze. Approaching the sofa triggers Bram's battle. Ivo demands victory in a rune-console game: Pet House becomes The Mending, a compact body-horror exploration puzzle. Winning persists through a later boss-battle loss. After his own defeat, Ivo admits the theft, walks to a cupboard and hands over the necklace. Full-bag retries and older completed saves are supported. The real party is untouched by the minigame. All other maps, species and necklace/vault progression remain. See Development/validation_hideout.md.

## Demo 1 / 0.8.1 — 24 September 2026

Regional Ekans and Arbok are now gray Normal/Dark forms. South Coast Road wild Ekans use form 1 and evolve into form-1 Arbok at level 22. All Poison-type level-up/tutor/egg moves are replaced with Dark moves; stats and abilities are unchanged. Ordinary owned snakes remain intact. Front/back/icon art and provisional matching shiny sprites use exact palette edits. Data, PBS, embedded encounter hook and Bible 1.28 are synchronized. Tests/regional_snakes.cjs verifies native Pokémon creation, evolution, inherited egg moves and save roundtrips; no graphical Mac playtest was performed. Included in the 0.8.1 Mac and editable-project packages.

Northern forest (The Listening Wood, map 103): Aipom replaces Caterpie in tall grass at the same 45% encounter weight and levels 3–5. Weedle (40%) and regional Wurmple (15%) remain. The encounter generator, PBS and compiled data agree. Existing companions and saves are unchanged. Included in 0.8.1; the older 0.8.0 downloads remain unchanged.

## Demo 1 / 0.8.0 — 23 September 2026

The opening caption now adds “Take it for a little walk, 100 steps.” This is wording only: guide Natu to the bed as before; no step counter was added. Pokémon losing their HP are described as having died, including field poison, while the existing battle and astral mechanics are retained.

Shiohama's three cottages use salt-weathered dark timber and stone footings. Window glass and its warm light stay aligned. The lighthouse artwork is unchanged. South Coast Road has a visible level-8 Tidebound Psyduck near the shallows, in addition to its existing rare grass encounter. Regional Psyduck now evolves into Whyduck at level 16; an older regional duck above 16 evolves at its next level-up. Ordinary Psyduck still evolves into Golduck at 33.

The docks now have two wooden sailing ships, sixteen new sailors including a captain, cargo stacks, a sailing notice, a ledger and a modest memorial. Nell (Wingull 8, Wooper 9) and Oren (Poliwag 10, Krabby 11) offer optional battles and remember a win. These use the existing astral-loss flow; neither is required for the story. Other sailors discuss trade, letters, watches, mountain settlements and everyday coastal life without explaining the late mythology.

Speak to the captain at the end of the eastern pier about **Psyduck Island**. Accepting reaches the demo's ending message. You remain in the docks and can continue exploring and saving. The island and voyage gameplay are future content.

Continue preserves existing party, inventory and quest flags. Updated map data reloads on old saves; a player standing where a new dock actor was placed is moved to a nearby clear tile. New Game is required to see the opening caption. The previous 99 starting Rare Candies remain available for evolution testing; this release does not remove user-requested supplies. Keep a backup before overwriting a save with a new journey.


Glaciverm is implemented: regional Wurmple's fixed personality split selects
it or Frostcoon at level 10. Ice/Bug, BST 435, Technician; native
priority moves and Coil. New front/back sprites and party icon are included.
Frostcoon has manually recoloured Silcoon sprites, authored defensive stats
and Shell Armor. See Development/validation_frostcoon.md for the new checks.
Its future level-55 Ice/Dragon evolution is recorded, not implemented.

Ordinary Wurmple, previous custom species, maps, quests, encounter rates, saves,
Mac runtime and font configuration remain intact. No GitHub sync configured.
Native test scope and platform limitations: Development/validation_glaciverm.md.


0.7.7 is a small visual refinement: Glaciverm's front view now has Wurmple's
rounded cream mouth. The party icon and shiny front also include it. Eyes,
horn, armour, body, rear view and all gameplay data remain unchanged.


0.7.8: The existing pier apparition now uses a manually edited Water/Ghost
Lapras: pale body, grey shell, green eye, small faded-yellow forehead mark and
sparse pixel mist. Battle sprites and party icon are included. Ordinary Lapras
and existing saves remain unchanged; later recruitment is still future content.


0.7.9: Glaciverm now has Wurmple-like yellow eyes and a deeper central
snout notch forming two rounded lobes. Front/shiny front and party icon updated.
Rear view and all Pokemon data remain unchanged.


Historical 0.7.10 (moves superseded below): Frostcoon is now an authored Bug/Ice cocoon with blue frozen-silk sprites,
a yellow eye, BST 350, Shell Armor and a complete level-up moveset through 54.
The level-55 Ice/Dragon remains future content. Existing Frostcoon keep their
identity, moves, HP and status while cached stats/old Shed Skin update on load.


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


0.7.14: Nature and environment revamp. The Listening Wood now has enclosed,
varied tree canopies, saplings, undergrowth, grass clearings and an irregular pool.
Shiohama has connected rocky outcrops, coastal rubble, offshore skerries and small
flower beds beside the lighthouse. The south road has clustered coastal woodland
and grass pockets; dockside courtyards gain planted areas. Animated sea colours
step from shallows into deeper water. Perpetual night and warm window lights remain.
Existing quest events and routes stay in place. Old saves standing in new scenery
move to the nearest safe connected tile once per affected map. Party, inventory,
quest state, death records and the new-game 99 Rare Candies remain intact.
See Development/validation_landscape.md for checks and platform limits.


0.7.15 (17 September 2026): Dense, overlapping tree blocks now define forest
clearings and coastal routes. Contiguous boulder piles enclose the headland and
road edges. Cropped small-rock fragments have been replaced by complete sprites.
The lighthouse cue now touches its doorstep; all 22 transition cues use exact
map-tile coordinates rather than character-sprite offsets. Night, quests,
encounters and Pokemon data remain unchanged. Landscape migration revision 2
safely moves old positions out of new scenery, including saves from 0.7.14.
Continue your existing save. Details: Development/validation_density.md.


0.7.16 (17 September 2026): Lighthouse interior refinement. The bedroom gains
complete furniture, a reading corner, rug and night windows. The hall has a
proper kitchen, sitting area, dinner table and pet resting place. Complete
stairwell sprites identify every level. The lantern room has a brass-and-glass
beacon whose lens lights when the existing oil quest is completed. The cellar
and vault use stone walls, storage bays and a clear central aisle. Existing
household scenes and quest routes retain their coordinates. Continue a saved
game; a position covered by new furniture moves to a nearby safe tile.
Pokemon data, outside maps and Bible 1.19 remain unchanged.


Earlier milestone 0.7.17: NEW GAME began in a small, one-time bedroom maze. Follow arrows,
stop on diamonds and use round teleport patches to find Wick. Mother's call
returns you to the familiar small bedroom, then the main-hall scene continues.
The paper beside the bed explains the symbols. No battles or penalties.
Continue works inside the maze; existing journeys skip it. The later psychic
projection explanation is recorded in Bible 1.22, not revealed in dialogue.
Mac build 26; save folder unchanged.


Earlier milestone 0.7.18: New Game began in a false ordinary bedroom. Inspect its furnishings, solve three bed questions, choose twelve years of sleep, and speak to Wick to enter the existing maze. Existing saves continue normally. There is no real-time waiting.


0.7.19: First-room books replace the computer. Sleep choices take place on the bed. The stairs visibly fold you back into the room. A hidden Water curse leaf has optional full-screen fractured text. Wick leads to a larger second bedroom; find its bed and solve four riddles in a row. Any wrong answer returns you to that room's beginning. Success enters the established Natu maze. Existing later journeys do not replay the prologue.

0.7.20: New Game begins with a sleeping Natu in darkness. After it opens one eye, guide the bird with directional keys through the dim paths to the sleeping child. This short prelude leads directly into the existing first bedroom. No saving is offered during this brief scene; Continue retains your existing journey.

0.7.21: Raised the existing original music loops and aligned exploration, battle and victory levels. Saved games and the in-game music slider still work.

0.7.22: Rare shore Psyduck on the southern road is Water/Psychic and evolves at level 33 into Whyduck (Water/Psychic), with hand-drawn Gen 3 style sprites and a psychic move progression. Existing ordinary Psyduck and Golduck retain their forms.

0.7.23: Whyduck now has hand-drawn open-skull green brain, a penguin-like confident stance and outstretched arms in front/back, shiny and icon artwork.

0.7.24: Approved Whyduck artwork: a pink brain, original Psyduck eye, hand and bill pixels, down-left gaze and a mirrored casting pose. Other gameplay is unchanged.


## GitHub migration — 24 September 2026

Prepared for the public ziemniaki/tidebound repository: current 0.8.0 source, assets, bible1.27 and guide2.25; old release archives and archived test evidence are excluded. The Mac game archive is unchanged. See Development/REPOSITORY_WORKFLOW.md. Migration verified on 24 September 2026: all 7,964 current files were cloned from public GitHub commit `19780315bf4227f24ab9b5ccdf6d8ee54b6e773e` and compared with the prepared release snapshot. Only standard Git text line-ending normalization differs; all build-manifest hashes pass. The one-time import workflow completed successfully and removed itself. GitHub `ziemniaki/tidebound` is now the authoritative working project.
