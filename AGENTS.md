# Tidebound — developer guide

**Repository handoff — 24 September 2026:** use `Development/REPOSITORY_WORKFLOW.md` for the new GitHub workflow. Initial import is current Demo 1 / 0.8.0 only. Migration is complete and verified at source commit `19780315bf4227f24ab9b5ccdf6d8ee54b6e773e`. GitHub `ziemniaki/tidebound` is authoritative. Older statements below about ZIP-only logistics are historical and superseded. Do not depend on conversation memory.


**Guide version:** 2.30, 26 September 2026
**Project baseline:** Demo 1 / 0.8.5, Pokémon Essentials 21.1
**Status:** existing game, continuing development; do not start over.

Place this file in the game project root, beside `Game.rxproj`, `Game.ini`, and
`Development/`. Paths below are relative to that root. This document describes
the delivered 0.8.0 baseline. After subsequent changes, update its affected
sections so it remains accurate.

## 1. Mandate and first-session instructions

We are developing a complete, original Pokémon fangame with the user as creative
director. The project grew from a detailed worldbuilding conversation and now has
a working opening. Continue that project. Do not substitute a generic Pokémon
game, a browser remake, a FireRed ROM hack, or a new engine.

The user wants continuity across devices and coding sessions. Treat checked-in
files as the durable project record. Do not assume access to earlier chats,
previous agents' working directories, or complete personal memory.

At the start of a new session:

1. Read this file, `README.md`, `PROJECT_STATUS.md`, `START_HERE.md`, `Development/README.md`, and the source files
   relevant to the task. Read `Development/design_bible.md` for narrative work.
2. Inspect the actual checkout and any uncommitted changes. Preserve the user's
   edits. If no Git repository exists yet, record that fact; do not claim that
   GitHub synchronization is already configured.
3. Identify the current milestone and the requested outcome. Distinguish what is
   implemented from what is merely planned.
4. Inspect the available tools in this workspace. On 9 September 2026 the user
   reported that an app update stopped their local Codex/ChatGPT development app
   from running on the older Intel Mac. Continue development here through the
   phone app. The Mac remains the target for downloading, testing and playing.
   Do not assume local Codex works or require a computer replacement.
5. Make a focused, reversible change, verify the relevant behavior, and update
   the project record. Ask only when a missing decision materially affects the
   result. Routine implementation choices do not need repeated confirmation.

Preserve and understand the existing baseline before making changes. After the verified GitHub migration, the repository is authoritative.
See Development/REPOSITORY_WORKFLOW.md. Release ZIPs are distribution snapshots.
The game bible and developer guide live in this tree. Do not introduce a large refactor or engine upgrade because the local
development app is unavailable.

## 2. Vision and boundaries

The game should feel dark, sad, nostalgic, haunted, and deeply solitary. Japanese
coastal horror and Dark Souls inform its emotional structure. The sea is central:
a majestic, disturbing presence, with occasional moments of extraordinary beauty
and hope. Horror should grow through attachment, implication, altered familiar
places, and consequential encounters. Darkness alone is not atmosphere.

The player forms relationships with vulnerable people and individual Pokémon.
Quests include riddles, exploration, sad dialogue, and attempts to help that
sometimes fail. There are relatively few trainer battles. The principal external
threats are predatory criminals and dangerous wild Pokémon; later, water demons
reshape the conflict.

Established structural decisions:

- The player lives in a lighthouse. Their elderly mother is its sole keeper.
- There is no conventional professor, rival, or eight-gym opening journey.
- Shrines of old masters replace gyms. Many later shrines are empty; special
  incense summons their masters for a battle that can grant a power.
- Dive is required for the eventual exploration design.
- Natu is the common regional bird. A special item will enable an evolution
  beyond Xatu. This species and its requirements remain to be designed.
- Poison has a major narrative and defensive role. Conventional poison cures,
  Full Heals, and ordinary Pokémon Centre recovery do not fit the intended loop.
- Death can lead into an astral world where companions may be recovered or lost.
- The full game remains finishable without the intended Suicune solution, but
  its ending is darker. Do not turn that route into an accidental softlock.

`Tidebound` is a working title. Ren, Wick, Shiohama, and other prototype names are
provisional. The confirmed opening style closely resembles Gen 3. Existing stock assets remain placeholders for eventual regional art.

### Presentation and pacing contract

**Confirmed period direction:** no advanced electronics in the story environment. Use books, craft, runes and magic. Keep the past implicit. Steampunk is a possible later motif, not implemented canon. Stock engine assets/interfaces may remain in the distribution; do not expose electronic PCs in authored scenes. The early dream rooms are expressly approved exceptions to gradual strangeness.

**Confirmed world rule: perpetual night.** Ordinary locations always take place at night. Retain the grey, dark, desaturated mood of the earlier opening; the brighter, cheerful autumn treatment in 0.5 is superseded. Autumn appears through worn foliage, stone, shore texture and small flowers under moonlight. Use charcoal, slate, cold grey-blue water and restrained traces of colour. Small lamps and sheltered interiors may offer warmth without turning the landscape into daylight.

Daylight or unusually bright surroundings are reserved for specifically approved magical locations later in the game. Do not add a normal day/night cycle, sunrise, or host-clock-dependent brightening. This is a firm world and presentation rule. Its narrative cause has not been established; do not invent one or reveal a supposed explanation in early dialogue. Ordinary battle scenes and time-of-day queries should also use night.

**Confirmed direction: familiarity before strangeness.** The opening should feel almost like a vanilla Generation 3 Pokémon reskin. Preserve its tile scale, familiar silhouettes, readable paths, movement and ordinary dialogue presentation. The coastal palette is dark and desaturated: slate rock, grey-blue sea, muted foliage, weathered timber, dim flowers and small amber lamp accents. Comfy autumn JRPG pixel art meets the sorrow and unease of Dark Souls and Twin Peaks. These are tonal references, not a request to copy their assets.

Introduce deeper mechanical changes, unusual scripts, animation and stronger visual departures progressively through the journey. Let the player first grow attached to a recognisable world. Early effects should serve a specific scene: a dog reacts to nothing visible; a quiet camera movement reveals more sea; a pale presence slowly becomes perceptible. Avoid front-loading a catalogue of custom systems or constantly advertising how modified the game is. Existing recovery mechanics remain in the prototype; this rule governs presentation and future pacing, rather than removing established mechanics.

**First coast, implemented in 0.5.** An irregular rocky lighthouse islet connects to the village by a worn stone causeway. Boulder clusters enclose the headland; a sandy beach sits in the sheltered bay. Muted autumn trees, flowers sheltered by stones, scattered shore rocks, sea glass and tended lamps provide signs of continuing care. The long timber pier faces an expanse of water; the map edge must stay outside every reachable view, including the encounter camera. Pookie's first bark reveals nothing. The later Lapras glimpse uses a pause, quieted music, gentle camera travel and a gradual appearance and disappearance.

**Later regional palettes remain proposals.** Forest greens and pale refuge light; clean winter whites before purple and green contamination; desaturated astral fog with recognisable companion colours. Keep terrain and interactive objects legible.

### Narrative authority and safeguards

`Development/design_bible.md` is the consolidated game bible, version 1.30,
26 September 2026. Its separate download is `Tidebound_Design_Bible.md`; a reading
PDF is also maintained. Keep packaged and separate copies synchronised. Its
confirmed decisions govern lore; proposals and open questions are not canon.
Do not treat working names or implementation conveniences as binding facts.

The following decisions have architectural consequences and must survive the
handoff: the real Koga remains missing; the corrupted Koga is a conjured poison
imitation with a different team; the protagonist was an existing person imbued
with water magic, unlike that imitation. Lapras progresses from frightening
apparition to beloved companion, with unsettling revelations later. Restored
Suicune becomes Water/Grass and can use a unique mystic sabre to access Behemoth
Blade for the intended final confrontation. The late cemetery master draws on
actual lost companions. The sea entities have a human history, and the player's
ultimate protection of living people must not erase that moral complexity.

Do not invent answers to deliberately unresolved mysteries to simplify a quest.
Do not reveal late-game information in early dialogue, item descriptions, or
interface text. Update the bible when narrative decisions are accepted.

## 3. What exists, and what the evidence establishes

The current archive is `Tidebound_Project.zip`. The extracted project is
`Tidebound_Prototype`, opening 0.7.24. The separate playable Mac distribution is
`Tidebound_Mac_0.7.24.zip`, containing `Tidebound.app`. The project retains its
Windows runtime and includes an upstream Mac template, matching runtime source,
and a repeatable Mac packager. Both distributions use the same game scripts.

**The user confirmed that the native 0.3 Mac app works on their Mac, then reported clipped text.** Version 0.4 fixes the reproduced engine font-metric issue with `fontHeightReporting: 1`. This user report is not an exhaustive playtest; the agent cannot execute macOS here.

The build's original `BUILD_MANIFEST.json`, `START_HERE.md`, and validation report
say that the producing agent did not run a graphical Windows playtest. Those are
historical statements about the build process. They do not negate the user's
later report. Preserve the distinction in future status updates.

Implemented opening:

| Map ID | Name | Function |
|---|---|---|
| 101 | The Keeper's House | Mother's talk, Maku's boxes, walk return, companion choice, journal |
| 102 | Shiohama | Lighthouse exterior, village, oil-shop entrance, pier apparition |
| 103 | The Listening Wood | Traveller's fire, Natu, dangerous pool, northern endpoint |
| 104 | The Lantern Room | Main lamp and unexplained downward-facing lamp |
| 105 | Beyond the Shore | Astral arrival, roaming spirits, guide, memorial, return |
| 106 | The Oil Shop | Elderly seller, oil collection after unlocking, return door |
| 107 | Your Room | Ordinary bedroom after the maze; main-hall exit |
| 108 | The South Coast Road | Optional Natu/Zigzagoon, first thief, storehouse approach, limited rest |
| 109 | The Old Storehouse | Overheard Abyss conversation, runner and second thief, necklace recovery |
| 110 | The Lighthouse Cellar | Stairs, stores, iron vault entrance |
| 111 | The Lighthouse Vault | Mother and seller, necklace storage, museum invitation |
| 112 | The Docks | First quay, warehouses, museum approach |
| 113 | Dockside Museum | Public sabre exhibit and ordinary coastal history |
| 114 | Your Room | One-time psychic maze |
| 115 | Your Room | First false bedroom; book cupboard and twelve-year sleep |
| 116 | Your Room, Again | Distorted second bedroom; four-riddle bed and reset route |

New Game first runs the one-screen Natu prelude, then starts at map 115, `(7, 8)`, with no party. Solve the false room, sleep twelve years, and speak to Wick to enter the larger second room (116 at `(7,22)`). Reach its bed and answer four consecutive riddles to enter map 114 at `(5,20)`. Find Wick in that maze.
Mother calls; return to map 107, the normal bedroom. The maze never reappears
in that journey. Its psychic origin is late lore. In map 101,
Maku moves boxes during Mother's talk. Pookie sleeps outside the lighthouse.
Walk her for 100 actual outdoor steps and return home together. Approaching
the pier optionally sends her running to its end; speak to her to resume.
Skipping the pier must still permit completion. No Lapras is visible in that beat.

Mother permits a choice of Natu/Wick, Makuhita/Maku or Poochyena/Pookie, level 7.
The other two individuals stay home. Eight Poke Balls are given once. Only then
is oil requested. The seller waits outside his locked shop; retrieve its keys
from white flowers in the northern forest, return them, watch him enter, then
enter to obtain oil. Mother receives the bottle and teaches the upstairs lamp.
The forest gate requires a chosen companion; requiring the lamp would now
softlock the keys quest. No mandatory combat precedes selection or key recovery.
Makuhita has Foresight for Ghosts; Natu has Night Shade and Poochyena has Bite.
Optional forest encounters remain a level-4 Natu and level-12 Frillish.

Mother is a believer in the water mythology; her ritual was not solely for the
child's benefit and keeps the protagonist a child. Guilt explains overprotection;
her own age forces her to prepare and release the child. Keep these truths as
late lore. Early dialogue offers exploration and teaching while Mother has time,
with restrained remarks about unchanged youth from elderly residents.

`story[:household_pets]` stores the actual unchosen Pokemon objects, with stable
identities. Choosing transfers that individual to the party and removes it from
the household hash. A chosen pet cannot be replaced after death by choosing again.
Opening revision 4 skips the new prologue and unlocks the shop for existing
0.3 saves, preserving their individual pets, selection, oil progress and losses.
Native Followers data stores Pookie during an active new-game walk. Only the
follower named `Tidebound Pookie` belongs to this quest; never clear all followers.
The step hook counts completed village movement only while following.
`TIDEBOUNDOILKEYS` is a non-consumable Key Item in pocket 8; it is removed on
delivery, and the persistent unlock opens the shop.

Legacy 0.2 saves are recognized by opening_started without opening_revision:
they retain companions and progress, receive no new household pets, and keep the
old oil-quest completion path. Migration must not infer a new game from an empty
party: an empty party can mean an unresolved astral loss.

The opening includes a custom title, fixed atmospheric lighting, fog, two
original ambient loops, limited recovery, identity-preserving spirit recovery,
and permanent loss records within the saved timeline. Lapras currently uses a
pale stock icon; no regional Lapras species/form or final sprite is implemented.

**Not implemented as playable chapters:** the regional dex, new evolution,
Koga's settlements and quest, later Team Abyss chapters, shrine progression, Dive
routes, corrupted/restored Suicune, sabre quest, final cemetery battle, final
water demons, and ending scenes. Some corresponding state helpers exist in
code; helpers are not completed gameplay.

## 4. Code and content ownership

The current custom source is in `Development/`, not in `Plugins/`:

| Path | Responsibility |
|---|---|
| `Development/001_Core.rb` | Engine-independent state, identities, spirit lifecycle, rest, memorials, planned ending state |
| `Development/002_Essentials.rb` | SaveData registration, battle integration, pre-heal snapshot, capture interception, guide and return |
| `Development/003_MapPassages.rb` | Generated passage masks for the thirteen story maps |
| `Development/004_Opening.rb` | Opening dialogue, event methods, story flags, transfers, atmosphere and passage hooks |
| `Development/005_Presentation.rb` | Household/follower sprites, crate/keys, apparition, lamps and title |
| `Development/006_FirstWalk.rb` | Bedroom/hall scenes, native Pookie follower, step counter, pier branch, keys and unlock |
| `Development/007_Coast.rb` | Coastal coordinate helpers, additive save migration, camera and Lapras staging |
| `Development/008_NeighborQuest.rb` | Pie/plate/necklace state, domestic scene, robbery, pursuit, NPC trainer rosters, seller return |
| `Development/009_NeighborPresentation.rb` | Ordinary plate/pie table prop and a faint local pearl highlight |
| `Development/rebuild_neighbor_data.py` | Three Key Items and three trainer types, compiled/PBS definitions and reference icons |
| `Development/rebuild_opening_items.py` | Matching PBS and compiled Oil-Shop Keys definition |
| `Development/rebuild_maps.py` | Authoritative generated map layouts, events and passage definitions |
| `Development/rebuild_scripts.py` | Embeds custom Ruby and updates selected project metadata |
| `Development/validate_maps.py` | Opening connectivity, arrivals, interactions, assets and embedded-source checks |
| `Development/package_mac.py` | Builds the native app from the included runtime and current game files |
| `Runtime/macOS/` | Unmodified runtime template, matching source, provenance and Mach-O inspection |
| `Development/Tests/` | Mechanic tests and native-object smoke harness |
| `PBS/` | Editable Essentials definitions alongside compiled `Data/` files |
| `Graphics/`, `Audio/` | Runtime artwork and sound |

`Data/Scripts.rxdata` is a compressed Ruby Marshal script archive. The rebuild
script inserts numbered custom Ruby files, in filename order, immediately before
Essentials' `Main` entry. The executable uses the embedded scripts. Editing the
text files alone does not update what the game runs.

**Do not also install the same custom code in `Plugins/Tidebound`.** That would
load it twice. The current rebuild script explicitly rejects that arrangement.
A later switch to a plugin architecture requires a deliberate migration that
removes the old loading path and verifies a single load.

Most stock engine source remains inside the script archive.
`Development/Tests/prepare_reference.py` extracts readable reference files into
`Development/Tests/engine_reference/`. These are inspection copies. Editing them
has no effect on the running game.

`collisions.json`, `map_manifest.json`, map preview PNGs and `event_scripts.json`
are generated artifacts. The JSON files are not currently the editable map
layout source. Do not change a generated report and expect gameplay to change.

## 5. Current mechanics and invariants

### Death and identity

`Tidebound::State` owns the realm, journey counter, current souls, permanent
memorials, story state and checkpoint. Pokémon receive a per-save
`@tidebound_identity`. A species name alone cannot identify a companion.

The current death route begins when the entire party loses or draws a wrapped
living-world battle. It does not impose permanent death on every individual
faint during an otherwise successful battle. Eggs and nested astral entry are
outside the supported prototype path.

Essentials normally heals the party after a permitted loss. The adapter captures
the party before that cleanup through `BattleCreationHelperMethods.after_battle`.
It then creates the spirit records and clears the living party. Preserve this
ordering; taking the snapshot after cleanup would defeat the recovery design.

Preserve the original individual's name, owner, personal ID, form, IVs, EVs,
moves, held item and relevant history. Recovery returns a copy of the archived
individual, not the engine's newly caught and potentially renamed/re-owned copy.
The battle opponent carries no item. Capture interception must not duplicate a
companion or its item into a party or storage box.

A spirit follows `waiting → engaged → recovered` or `waiting/engaged → lost`.
Only one encounter can be active. Leaving marks unresolved spirits as lost.
Repeated deaths must not duplicate identities or memorial entries. A technical
exception must not be deliberately counted as a narrative failure; preserve the
existing rollback behavior and investigate any uncovered failure window.

### Scope of integration

Use `Tidebound::Opening.fight` for the current opening's living-world encounters.
It calls `Tidebound.wild!` and performs the map transfer if the result is `:astral`.
Calling `Tidebound.wild!` directly requires the caller to handle that return value.
Do not launch an ordinary `WildBattle.start` and assume the custom death route
will apply. `Tidebound.trainer!` now wraps native `TrainerBattle.start_core` with
exactly the same pre-heal snapshot rules. `NeighborQuest.battle` handles its astral
transfer. Only outcome 1 advances trainer victories. Loss, draw or an aborted
battle must leave that opponent retryable. The grass-entry WildBattle.start path on maps 103/108 also uses this wrapper through 010_FieldDetails.rb. There is still no global blackout replacement; other event authors must explicitly use these wrappers.

`Tidebound.recover_spirit!` resolves a spirit encounter.
`Tidebound.return_to_living!` returns checkpoint coordinates; its caller performs
the actual transfer. Keep state transitions separate from presentation where
practical. Do not scatter competing death handlers across map events.

### Provisional balancing, not settled rules

| Setting | Current implementation |
|---|---|
| Fire rest | Full HP and PP once per fire per 900 real seconds; status unchanged |
| Astral recovery and return | HP floor of 25%, rounded up; never reduces existing HP |
| Exhausted moves on astral return | One PP floor; fire rests instead restore all PP |
| Status at rest | Does not cure poison or other status |
| Spirit opportunity | One encounter, ending after six unresolved rounds |
| Spirit catch rate | Engine catch-rate parameter 35; this is **not** a 35% probability |
| Astral guide | Borrowed Natu, scaled to highest fallen level, healed after spirit battles |
| Astral balls | 18 Poké Balls supplied once per journey |
| No surviving companions | A different level-5 Natu permits continued play |
| Saving | Manual; loading an older save can roll back a loss |
| Cemetery helper | Copies up to six most recent losses; fills vacancies with supplied fallback Pokémon |

The guide, fallback bird, supplies and exact balance values require later design
review. They prevent an unplayable prototype; they are not permanent lore.

`Config::BLOCKED_ITEMS` is a list, not an implemented global ban. The opening has
no healing shops or Centres, but future item distribution, berries, held items,
abilities, moves, PC behavior and scripted heals need a deliberate audit.
Do not report the final no-cure system as complete. The precise treatment of
status-curing moves and abilities remains to be decided.

The ending helper currently checks story flags for healed Suicune, sabre and
final victory. It does not prove that the individual is present, has the item,
or used the move. Connect the eventual encounter and ending to actual gameplay
state; do not mistake this scaffold for a complete final-boss implementation.

## 6. Save compatibility

Custom state registers with Essentials as `:tidebound`. The top-level alias
`TideboundSaveState = Tidebound::State` is intentional. Essentials 21.1 validates
`ensure_class` using a symbol constant; the nested symbol `:"Tidebound::State"`
failed in the native save test. Preserve the alias or replace it with an
explicitly verified compatibility solution.

The current schema version is 1. Persistent Ruby class names, identity fields,
map IDs and story keys matter to existing saves. Do not rename or remove them
without a migration or a clearly stated incompatibility decision. Increasing a
schema number alone does not migrate data. Never silently reset a player's save
to make a development error disappear.

The configured save-directory name is `Tidebound_Opening_0_2`. Do not change it
incidentally while updating a title: saves can appear lost when the directory
changes. Keep a copy of a working save before investigating compatibility.

Release version and `Tidebound::VERSION` are both 0.8.5. The global state schema
remains 1; the opening's additive migration uses story opening_revision 4.

## 7. Build and map-editing discipline

**Build/release update:** `Development/RELEASING.md` now governs packaging.
Windows player packages reuse the pinned existing x64 executable/DLLs.
`Tests/windows_runtime_smoke.py` and the Mac wrapper share
`Tests/native_runtime_smoke.rb`; inject it only into disposable copies.
Release CI requires native smoke on Windows x64 and both Mac architectures.
`release.json` pins runtime inputs and package versions. The universal Mac package
is staged and ad-hoc signed on macOS, then tested by native ARM/Intel CI jobs.
`Development/check_rebuild.py` runs generators in a disposable tracked-file copy.
Version tags prepare draft releases after all gates; the old pond publisher is
retired. Older references to a Python-standard-library-only Linux Mac packager
are superseded. Preserve `Tidebound_Opening_0_2` and the Monterey target.

**Current developer entry point:** follow the fresh-clone setup in
`Development/README.md`, install `requirements-dev.txt` and the locked Node test
dependencies, then run `python Development/verify.py` with the virtual environment
active. This is also the PR CI gate. It does not rebuild tracked game data.
`validate_maps.py` is read-only unless `--event-scripts PATH` explicitly requests
an event report. After intentional map edits, refresh the tracked report using
`--event-scripts Development/event_scripts.json` from the repository root.
Duplicate/custom script ordering and the competing `Plugins/Tidebound` load path
are rejected; the rebuilder checks the plugin conflict before writing files.
Historical version sections below are context, not additional setup steps.

Use a project-local Python environment if dependencies need installation. The
rebuild tools require Python 3, `rubymarshal==1.2.10`, and Pillow. Optional audio
regeneration also requires NumPy and ffmpeg. Python and Node are development
tools; neither is required to run the supplied Windows game.

For a custom Ruby change, from the project root:

```sh
python3 Development/rebuild_scripts.py
python3 Development/validate_maps.py
```

For an intentional generated-map change:

```sh
python3 Development/rebuild_maps.py
python3 Development/rebuild_opening_items.py
python3 Development/rebuild_neighbor_data.py
python3 Development/rebuild_field_data.py
python3 Development/rebuild_scripts.py
python3 Development/validate_maps.py
```

**Read the scripts before running them on a changed checkout.**

- `rebuild_maps.py` overwrites maps 101–109, their masks and map reports, and
  updates the start position and metadata. It can erase map-editor changes.
- Passage masks, rather than only native tile passage settings, govern these
  maps. Changes to geometry must keep visual layout and collision consistent.
- `rebuild_scripts.py` also rewrites selected global metadata, battle music and
  the generated section of `PBS/map_metadata.txt`. It is not a pure Ruby packer.
- It reconstructs everything after its `# TIDEBOUND OPENING MAPS` marker. Do not
  append unrelated hand-authored map definitions there and expect them to survive.
- Version/title replacements and the validator are tailored to the opening.
  Extend those tools when adding modules or maps; do not assume they generalize.
- Keep PBS definitions and their compiled counterparts consistent. The custom
  Ruby rebuild is not a general compiler for newly added Pokémon or moves.

Choose one map authoring source for each map. The present opening uses Python
layouts. If moving a map to RPG Maker XP editing, preserve the existing map,
remove or change its generator ownership deliberately, and reconcile collision
handling before continuing. Do not alternate blindly between both workflows.

### Required Mac playtest target and remote development

The user's computer is a 15-inch Mid-2015 Intel MacBook Pro running macOS
Monterey 12.7.5 (reported as "12.75"). The user reports that the updated local
development app no longer runs. Development therefore continues in this
phone-accessed workspace. Mac remains the primary testing and playing target;
Windows is secondary. The workspace itself is not the user's Mac.
Do not require a computer replacement or OS upgrade as a routine setup step.

The RPG Maker project is `Game.rxproj`. The native Mac bundle uses official
mkxp-z 2.4.2/826929e with Ruby 3.1; Windows retains its supplied 2.4.2/c9378cf
runtime. Essentials itself remains 21.1. The Mac build is from upstream dev,
not an unmerged pull request. Exact artifact, source and checks are recorded in
`Runtime/macOS/PROVENANCE.md` and `macho_report.json`.

All five Intel Mach-O images target macOS 10.13 or earlier. Linked non-system
libraries resolve inside the app. These checks establish deployment-target and
dependency compatibility, not a native Mac playtest. The upstream Intel binary
is unsigned; the app is not notarized. Use Monterey's per-app Open action when
needed. Never disable Gatekeeper globally or claim notarization.

Build a matching Mac distribution from the project root:

```sh
python3 Development/package_mac.py /path/to/new-output-folder
```

The Python-standard-library packager copies the current game into Contents/Game,
preserves native runtime bytes and permissions, and archives the app with ZIP
symlinks preserved. No Homebrew, Wine, Ruby installation or compiler is needed
to play. Rebuild after source changes; downloaded apps do not synchronize back
here. The save identity remains Tidebound_Opening_0_2, outside the app.

`MAC_README.txt` is the short player-facing launch guide. Source, runtime source,
documentation and build tools live in the maintained project. The Mac ZIP is the
ready-to-play distribution. Keep their game script hashes in agreement.

The actual Linux build from the same upstream commit rendered the 0.3 opening and
ran full engine save/load, battle defeat, astral transfer and return checks under
software OpenGL with scripted input. Audio
used a null output device; that does not establish audible playback. Native
Monterey launch, audio, keys and the full recovery loop remain an on-device gate.
The graphical map editor is a separate tooling question; retain the working
script-generated map workflow.

## 8. Verification and reporting

The current build passes 30 domain/adapter tests and a separate smoke harness using
actual Essentials Pokémon, moves, owner, player, bag, interpreter and SaveData
classes. That harness replaces graphics, messages, transfers and selected services with
fixtures. It additionally covers all three choices, cancellation, complete player/
household save round trips and old-save migration. Rendered-engine smoke evidence
is recorded separately in Development/validation_report.md.

From `Development/Tests/`, when its Node dependencies are not installed:

```sh
npm ci
```

Then run the relevant checks:

```sh
python3 prepare_reference.py
node run.cjs
node native_domain.cjs
```

Refresh the reference extraction after changing the embedded engine archive.
The Node harness uses Ruby 3.2 WASM; keep custom syntax compatible with the
shipped Ruby 3.1 runtime. A native Ruby installation can also run the basic
suite through `ruby Development/Tests/run.rb` from the project root.

The map validator checks the nine opening maps' connected paths, arrivals,
interactions, selected assets and embedded-source agreement. Its scope must grow
with the game. Preview PNGs are offline tile renders, not game screenshots.

For changes to recovery or persistence, verify relevant cases including capture,
failure, abandonment, zero survivors, six companions, a second death,
save/reload, identity/item preservation and technical-error rollback. For visual
or map changes, test the affected area on screen when the runtime is available.
Do not add redundant tests for every dialogue edit.

Report separately: implemented changes, automated evidence, actual playtesting,
and remaining limits. “The user says it works,” “the smoke harness passed,” and
“I played through this branch” are different evidence statements.

## 9. Direction for a larger codebase

Extend Essentials incrementally. Preserve separation between pure game rules,
engine integration, content and presentation. The current ten files are a
prototype organization, not a mandate to put the entire game into one opening
script.

As features arrive, introduce focused modules for quest progression, shrines,
regional forms, boss behavior and world changes. Prefer explicit state and
reusable event methods over unexplained global switches and duplicated scripts.
Use stable identifiers for quests, species/forms, assets and persistent actors.
A character's display name should not be its database identity.

Major quests should eventually record prerequisites, stages, transitions,
completion/failure conditions, affected NPC dialogue, map changes and recovery
behavior. Persistent world changes, such as a poisoned settlement, must survive
save/reload and remain consistent with the corresponding quest stage.

Keep art source files when available, alongside the exported assets the game
loads. Record palette, dimensions, animation frames, naming and attribution.
Use stock art for iteration only when clearly identified as temporary. Maintain
readable paths and interaction cues under darkness and fog. Do not compensate
for weak atmosphere with rapid flashes, unreadable scenes or relentless effects.

Extract dialogue into a more maintainable content format when its volume
justifies that work. Record save migration and build implications before a
large data refactor. No engine rewrite is authorized by this architectural
recommendation alone.

## 10. Repository and continuity workflow

The current agreed workflow is development here, with a regularly updated project
ZIP for the user to download to the Mac and separate maintained bible and guide.
A private GitHub repository remains a possible later improvement, not a blocker
or a currently configured service. Do not publish publicly or upload to an
unspecified account as an incidental setup step.

For each delivered revision, keep `PROJECT_STATUS.md` accurate, name the current
archive, and preserve source, required assets and build tools. Keep save files
separate from replacement project folders and never overwrite the user's saves.
If the user modifies their downloaded copy, obtain that changed copy before
building on it; do not assume it synchronises back here automatically.

Preserve the delivered archive and create a clearly identified baseline commit
when Git is established. Keep save files, credentials, installed dependencies,
temporary reference extractions and disposable caches out of version control.
Keep the source and required runtime assets available so a clean checkout can
reproduce a build. Do not ignore all `Data/` files: several are currently required
inputs, not independently rebuildable outputs.

Use focused commits and short-lived branches for substantial changes. Keep a
known working main branch. Avoid simultaneous edits to the same binary map.
Store release archives outside ordinary source history. Introduce Git LFS for
large binary assets if needed, and verify that the build environment retrieves
the real assets rather than pointer files.

Keep continuity lightweight. In addition to this document and the maintained
game bible, maintain a short current-status/next-steps record and a task list.
`PROJECT_STATUS.md` now records the migration status and immediate task list.
Keep it current; add other tracking files only when useful.
Record important decisions with their reason; clearly label proposals.

Phone discussions now guide development in this workspace. Record accepted
decisions in the maintained project documents and deliver matching copies in
the ZIP. Separate working copies need explicit synchronisation. Do not rely on
chat memory to resolve conflicting versions of code or lore.

## 11. Collaboration and next milestones

The user values initiative, imagination, direct explanations and concrete
results. Discuss creative choices in plain language. Keep routine status reports
short. Explain consequences before decisions that change the game's identity,
permanent-loss policy, platform, or established narrative. Avoid imposing a large
project-management apparatus before it is useful.

Current priorities, in order:

1. Preserve the full bible and developer guide as separate documents and matching
   copies inside the project. This documentation milestone is complete in this
   revision; continue to update them as decisions change.
2. Test the delivered native Mac app on the user's Intel Mac with Monterey
   12.7.5. Record the exact result; distinguish user reports from agent checks.
3. Maintain coherent downloadable project revisions. GitHub can be added later
   if useful and a specific private target is established.
4. Choose the next small playable milestone together. Improve and expand the
   game through complete, testable sections, using the bible's status labels.

The long-term objective is the whole game. The immediate responsibility of each
session is to leave a coherent, understandable and recoverable project for the
next session.


### 0.4 font compatibility

Keep `fontHeightReporting: 1` in the bundled `mkxp.json`. With the current
mkxp-z runtime, nominal TTF height cuts the lower half off Power Green glyphs.
Actual rendered-height reporting fixes Essentials' text-size/draw-rectangle
contract. Do not replace the fonts or add a second draw-text shim incidentally.

### Repository status checked for 0.4

The working 0.3 source archive matched its delivered SHA-256. No Tidebound
repository appeared in the connected GitHub account or installed-repository
search. Prior access to mkxp-z upstream was runtime retrieval, not a game-repo
sync. Do not claim a game repository has been secured or another model's edits
merged without locating and inspecting the exact repository.


### Coast geometry and saves in 0.5

Map 102 is now 108 by 88 tiles. Its layout uses local anchors plus offset (24,20).
`Opening.travel` always accepts native map coordinates. Only `travel_coast` and
`coast_xy` translate local coast anchors. Checkpoint coordinates stay native.
Do not add implicit translation to the general travel function.

Opening revision remains 4. A separate `story[:coast_revision]` becomes 5.
Old coastal saves shift the player and native follower records once. If a former
land tile is now water, migration selects nearby safe ground. The first eleven
coastal event IDs retain their identities; new decorations are appended. Preserve
Pookie's original event ID and the named follower. Map magic 26090905 refreshes
old cached map geometry. Keep schema 1, pet identities and save-directory identity.

The user confirmed 0.4 works. Version 0.5 uses the same Mac runtime and retains
fontHeightReporting 1. Native Linux engine checks are not a macOS playtest.


### Permanent night in 0.5.1

004_Opening.rb owns NIGHT_TONE (-80,-74,-48,150) for ordinary outdoor maps.
Interiors retain sheltered lamplight; the astral map keeps its existing fog tone.
TIME_SHADING remains false. The story-map day/night queries and battle setup
resolve to night independently of the host clock; normal elapsed timers continue.
DAYLIGHT_MAPS is empty. Add entries only for approved magical locations and author
their lighting and battle setting explicitly. Register new story maps in MAP_IDS;
do not let them silently inherit the stock demo's time-of-day behaviour.
This patch changes no geometry, quest order, save schema or coastal migration.


### Neighbour quest introduced in 0.6.0

The seller gives pie after the indoor oil handoff. Mother shares it in a short
household scene; the washed blue-reed plate becomes an ordinary Key Item. Returning
it to the shop triggers two boys fleeing south and the seller's failed chase.
The new road (108) has two optional wilds before the first thief, a narrow
crossing, a travelling ninja's fire and the approach to an old storehouse (109).
Overheard low-level conversation precedes battles with its runner and second
thief. Returning the pearl necklace reveals its deceased owner, one small glint,
and an incidental museum/Ellie/vault remark. No meal healing is granted.

Persistent state: `story[:neighbor_quest]` is an additive hash. `:stage` advances
nil → :pie → :plate → :pursuit → :necklace → :complete. Separate flags preserve
:first_won, :hideout_seen, :heard, :runner_won, :second_won, :shorebird_gone and
:shoreforager_gone. No global switch IDs or variable IDs are reserved by this
quest; Essentials retains its standard outcome variable 1. Save schema 1,
opening_revision 4, coast_revision 5 and external save directory stay unchanged.
Map magic 26091006 refreshes current map/event data without retranslating coast
positions. Do not bump coast_revision merely because new events were appended.
The original sixteen Shiohama event IDs remain stable, including Pookie's ID4.

An old save with oil already collected can obtain a belated pie by speaking to
the seller inside. It does not repeat keys, oil, walk, starter or lamp rewards.
Pie→plate replacement rolls back if the bag rejects the plate; a defeated second
thief keeps the necklace available if collection fails. A later visit then
collects it without another battle. Quest objects survive ordinary astral losses.
Transient scene props/busy flags are not saved. Native map creation restores
actor visibility from persistent state; hidden actors must also be through.

Trainer rosters use native NPCTrainer objects accepted by TrainerBattle.start_core,
not entries in trainers.txt. Edit ROSTERS in 008 for these three opponents. The
trainer types and three Key Items have reproducible PBS and compiled data in
rebuild_neighbor_data.py. Temporary bag icons reuse Lava Cookie, Shoal Shell and
Pearl String; their labels/descriptions are authoritative. The table's blue-reed
plate is a small code-drawn household prop, not a magical held Plate.

Implementation choices: Ellie is Mother's working name because none existed;
Toma, Ivo and Bram are provisional NPC names. The boys are from the surrounding
coast, preserving the starting village's elderly permanent population. The south
path unlocks after the robbery so the earlier walk/keys/lamp progression remains
focused. City 4 is mentioned literally as a working designation. The new road
and storehouse are local additions, not a City 2 map.

Bible 1.7 records future canon: City 2 shipping/salvage/fencing/distribution;
major museum displaying the unique sabre; later Abyss theft with incomplete
understanding; much later healed Suicune/Behemoth Blade/better resolution. Do not
build those chapters, explain the vault, or give early criminals knowledge of
the sabre's purpose. The necklace pearls belong to a recurring magical category;
neither the seller nor child knows that. Mourning here is healthy attachment.

See Development/validation_report.md for completed checks and limitations.
The native Mac runtime and fontHeightReporting=1 remain unchanged. This release
still requires the user's Monterey playtest. No GitHub sync has been established.

### Field refinements in 0.6.1

010_FieldDetails.rb owns fire cooldowns, berry collection/regrowth, native grass
terrain and battle routing, pale exit cues and untinted local amber lights.
rebuild_field_data.py owns PBS/encounters_tidebound.txt and compiled encounter
data for maps 103/108. Keep their authored grass tile 391 on layer 1 aligned
with the terrain hook. No encounter tables apply to ordinary path tiles.

story[:fire_rests] keys :wood_fire and :road_fire store Unix seconds. Fire
healing restores full HP/PP every 900 seconds per fire; status remains. The
checkpoint updates even during cooldown, without invoking the old rest floor.
Astral-return rest! remains the old floor and is a distinct rule.
story[:berry_picks] keys [map_id, authored_x, authored_y] store pick times.
Coast authored coordinates use local offset (24,20); tree visual code translates
back to those keys. Two Oran/Sitrus berries per pick, 3600-second regrowth.
Only a successful bag handoff consumes a harvest. Trees show unripe fruit after
picking. These quantities are implementation choices, not new mythology.

Map magic 26091007 refreshes cached map events. Schema 1, opening revision 4,
coast revision 5, original event IDs and save-directory identity stay unchanged.
Native Mac runtime bytes/font configuration are unchanged. User confirmed
0.6.0 works; 0.6.1 agent verification is Linux, not an on-device Mac playtest.

### Vault/museum chapter in 0.7.0

Read 011_VaultVisit.rb for the additive story[:vault_visit] state: gift, open,
talk and museum booleans. The existing neighbour :complete stage is unchanged.
Gift success is required before departure; a full bag leaves the seller/reward
available. Existing completed-necklace saves collect it by speaking to him.
Mother opens the basement in the hall. Actors use persistent flags to avoid
duplicating across the shop, house and vault, and return after the museum visit.

New maps: 110 cellar, 111 vault, 112 dock-city outskirts, 113 museum.
vault_maps.py is executed by rebuild_maps.py and shares its authoring classes.
012_VaultPresentation.rb draws the iron door, pillars, drawers and exhibit cases.
The new Blue-Reed Keepsake is a non-consumable Key Item registered by
rebuild_neighbor_data.py. The sabre remains scenery, never an acquired item.
Update both name and portion-name fields when cloning compiled item definitions.

Map magic 26091008; state schema 1, opening revision 4 and coast revision 5
remain unchanged. All prior event IDs retained. New maps use the same fixed
night/indoor tone system; no extra healing resources or encounter tables.
A passage beside the existing storehouse opens after the vault conversation.
Keep saves in Tidebound_Opening_0_2. Runtime and font configuration unchanged.

This explicitly supersedes earlier instructions to defer all museum/vault
interiors. Only this visit is authorized: sabre theft, powers and late lore
remain unimplemented. See Bible 1.8 section 20 and validation_vault.md.

### Entrance and dock refinements in 0.7.1

Essentials pbMoveRoute appends THROUGH_OFF. Opening.animate now restores the
actor's preceding through value after completion. Hidden departure actors must
set both opacity=0 and through=true. The runaway thief and departing oil seller
previously blocked their destination door tiles invisibly until map recreation.
Test real player steps into entrances immediately after cutscenes; a direct
map transfer cannot detect this collision bug.

013_DockDetails.rb replaces guessed window overlays with masks of actual glass
pixels from the native Outside tileset. Keep frames, wall and door pixels clear.
Pane sprites follow the map's exact subpixel camera position in a neutral
viewport. 010_FieldDetails.rb retains lamp/fire glows, without invented windows.

dock_details.py extends map 112 through vault_maps.py: paved lanes and forecourt,
brick houses, waterfront workshops, customs warehouse, lamps, boats and quay
props. Original museum and road transfers/event IDs remain stable. New closed
frontages have local dialogue; they are not unfinished transfer events. No new
interiors, healing systems or story chapters were added.

Map magic 26091201 refreshes cached maps; schema 1, opening revision 4 and coast
revision 5 stay unchanged. The additive story[:dock_revision]=1 migrates an old
dock save only if the player's tile is newly blocked, choosing nearby walkable
unoccupied ground. Preserve native Mac runtime and fontHeightReporting=1.
See Development/validation_docks.md and Tests/rendered_docks.rb. Native Linux
checks passed, including immediate doorway movement; Mac verification remains
the user's on-device check. No GitHub synchronization is configured.

### Regional Sunkern in 0.7.2

014_RegionalForms.rb applies form 1 to newly generated wild Sunkern on map 108
via on_wild_pokemon_created, then resets their level-appropriate moves. It never
rewrites party, storage or astral companions. Form 0 remains ordinary Sunkern.
rebuild_regional_data.py creates SUNKERN_1 in Data/species.dat and matching
PBS/pokemon_forms_tidebound.txt; run it before rebuild_scripts.py.

Grass/Dark typing; the original six base stats of 30 and abilities remain.
Level-up moves emphasize absorption, endurance and Dark attacks; sun-themed
level-up/tutor/egg moves are omitted. No custom Sunflora is authorized. The
existing Sun Stone evolution still yields ordinary Sunflora, with a narrow
species setter hook normalizing its form to 0. This is a provisional continuity
choice, not a final regional evolution or a new source of sunlight in the world.

Graphics/Pokemon/{Front,Back,Icons}/SUNKERN_1.png are generated from the retained
Development/Art/Sunkern/source.png. export.sh performs mechanical extraction,
16-colour reduction and nearest-neighbor scaling. Battle frames are 160x160;
the two-frame icon strip is 128x64. Shiny front/back currently share the regional
palette so the healthy form cannot appear as an accidental fallback. Separate
shiny colours remain undecided. Keep the art prompt and source attribution.

No map/save-schema changes. Existing saves work without starting over. See
Development/validation_sunkern.md for checks and platform limits.

### Moonkern in 0.7.3

The user approved a new Grass/Ghost evolution: the hollow spirit of a Sunkern
that could never sprout. MOONKERN is a distinct species with DefaultForm_0.
Only SUNKERN_1 now evolves into it at level 24; ordinary SUNKERN is untouched.
This supersedes the provisional regional Sun Stone-to-Sunflora rule above.
014_RegionalForms.rb no longer prepends a species setter: native DefaultForm_0
normalizes Moonkern after evolution and keeps existing identities intact.

rebuild_regional_data.py owns compiled species/metrics and the three PBS files
pokemon_forms_tidebound.txt, pokemon_tidebound.txt, pokemon_metrics_tidebound.txt.
Moonkern has reverse prevolution data; no forward evolution. Base stats in PBS
order HP/Attack/Defence/Speed/Sp.Atk/Sp.Def are 65/45/65/60/105/100 (total 440).
Abilities are Insomnia/Infiltrator, hidden Cursed Body. Hex is an evolution move
(level 0). Development/Art/Moonkern retains the built-in generated atlas, prompt
and ImageMagick export. Transparent hollow interior must survive export.
Battle frames 160x160; icon 128x64 with a small bob. Shiny art currently uses the
same palette. The cry temporarily reuses Sunkern's included cry, with credits.

No new maps, items or quests. No forced evolution or rewrite of existing saves.
Normal evolution cancellation and Everstone remain supported. A regional
Sunkern already at/above 24 qualifies on its next level gain. The ghost form
is a species evolution, never a substitute for the astral-loss system.
See validation_moonkern.md and Tests/rendered_moonkern.rb.

### Moonflora and simplified art in 0.7.4

Confirmed chain: SUNKERN_1 -> Level 14 MOONKERN -> Level 20 MOONFLORA. This
supersedes the former level-24/final-Moonkern rule. Ordinary Sunkern/Sunflora
remain unchanged. Native evolution advances one stage per event; existing
companions at/above thresholds qualify on their next level gain. No save
migration, new map, item or quest.

rebuild_regional_data.py calls rebuild_moonflora_data.py. Together they author
forward/reverse family links, species/metrics data and matching PBS. Moonflora
is a separate Grass/Ghost species with DefaultForm_0. It learns Shadow Ball
upon evolution. PBS-order base stats: 75/50/80/60/115/110, total 490. Abilities
match Moonkern; its existing stats remain unchanged.

The user rejected an overly detailed Moonflora draft. Keep the compact original
Sunflora proportions, simple petal ring, flat shading, small readable face and
no decorative aura particles. Art must work at native resolution alongside the
stock sprites. Art/Moonflora retains the revised source atlas, prompt and
mechanical export: 8-colour reduction, 38x46 logical battle art at 2x scale on
160x160 canvases, 128x64 bobbing party icon. Hollow face remains transparent.
The ghost is the flower it never physically became, not a resurrection.
Shiny art shares the normal palette; cry reuses included Sunflora provisionally.
See validation_moonflora.md and Tests/rendered_moonflora.rb.


### Regional Wurmple in 0.7.5

WURMPLE_1 is Bug/Ice and bright pale blue. 014_RegionalForms.rb applies form 1
only to newly generated wild Wurmple on map 103. Keep existing owned forms,
other-map encounters and the native forest rates/levels unchanged. Stats,
moves and abilities inherit stock Wurmple. rebuild_regional_data.py invokes
rebuild_wurmple_data.py, maintaining species.dat and the independent
PBS/pokemon_forms_tidebound_wurmple.txt suffix.

The user deferred evolution design. Retain ordinary Silcoon/Cascoon routes
provisionally. TideboundWurmpleEvolution normalizes form 1 to 0 only when this
Wurmple changes into those species, preventing an undefined evolved form.
Do not add regional evolutions or rebalance the line without a new request.

The user explicitly authorized direct pixel recolouring after image-generation
failures. Art/Wurmple/recolour.py maps exact palette entries in stock front,
back and icon images without altering geometry or alpha. It preserves the two
native icon frames. Shiny sprites share the blue palette provisionally.
No runtime filter, map changes, save migration or Mac runtime change is needed.
See validation_wurmple.md and Tests/rendered_wurmple.rb.


### Glaciverm and the level-10 split in 0.7.6

WURMPLE_1 now uses GLACIVERM,Silcoon,10 and FROSTCOON,Cascoon,10. These are
native evolution methods using the fixed high-word personal-ID modulo-10
split, approximately 50:50. No new RNG or save field. Both new species declare
DefaultForm_0; the obsolete TideboundWurmpleEvolution setter wrapper is removed.
Ordinary Wurmple keeps its level-7 branches. Old regional Wurmple above 10
qualify on their next level gain; never reroll or rewrite individual identity.

rebuild_wurmple_data.py invokes rebuild_glaciverm_data.py. The latter owns
PBS/pokemon_glaciverm.txt, pokemon_metrics_glaciverm.txt, compiled species and
metrics, cries and provisional cocoon art. Build regional data before scripts.
Glaciverm: Ice/Bug, stats in PBS order 75/105/110/40/40/65 (BST 435), sole ability
Technician. Native move rules remain unchanged: Ice Fang (65) and First
Impression (90) are NOT Technician-boosted. Coil starts at 24. Read Bible 25
for the full implemented move schedule and balance rationale.

Frostcoon is a distinct, provisional Bug/Ice species, working name. It reuses
Silcoon's white art, stats/ability and cry. No current further evolution. The
user confirmed a FUTURE level-55 Ice/Dragon pseudo-legendary; do not fabricate
that species or mark it playable before the later design request. No map,
encounter-rate, quest, save-schema, Mac runtime or font changes are required.

Art/Glaciverm contains the generated atlas and mechanical ImageMagick export:
12-colour reduction, compact nearest-neighbour battle sprites and bobbing icon.
Preserve the simple silhouette. Shiny currently shares normal art. Test driver
Tests/rendered_glaciverm.rb verifies actual PBS recompilation, both evolution
animations, moves, battle rules, identity/save/astral and sprites in a disposable
engine. It supersedes the historical 0.7.5 rendered_wurmple.rb evolution checks.
See validation_glaciverm.md; native Mac execution remains the user's check.


### Glaciverm mouth refinement in 0.7.7

Art-only refinement requested by the user: front sprite now has Wurmple's
rounded, protruding cream mouth and lip crease. Art/Glaciverm/mouth_detail.py
adds a small pixel cluster to exported/front.png; export.sh calls it before
battle enlargement and icon generation. It reuses existing colours and does
not modify eyes, horn, armour or body. Rear view remains unchanged because
it does not expose the mouth. Normal/shiny front sprites and both icon frames
are rebuilt. Retain the generated atlas and subsequent pixel-edit recipe.
No Pokemon data, balance, evolution rules, maps, quests or save logic changed.


### Ghostly Lapras in 0.7.8

LAPRAS_1 is the Water/Ghost Tidebound form. rebuild_lapras_data.py adds its
compiled data and PBS/pokemon_forms_tidebound_lapras.txt; it is also invoked
by rebuild_regional_data.py. Ordinary LAPRAS stays Water/Ice. Stats, moves,
abilities and cry inherit stock Lapras. No global wild-form hook is installed.

Art/Lapras/edit_sprites.py directly edits stock front/back and both icon frames:
white/cold-cream body, mist-grey shell, green iris, faded-yellow forehead scar,
sparse translucent pixel mist. Original opaque silhouette and dimensions stay
intact. Shiny front/back share this palette provisionally; no image generator.

005_Presentation.rb selects Pokemon.new(:LAPRAS_1,10) only for the existing pier
apparition. Its owned neutral viewport keeps the pale light visible under night
tint and is disposed with the sprite. Existing alpha fades, bobbing, camera,
dialogue and flags remain. Merely displaying it must not register it in the dex.
Pookie's earlier bark still reveals nothing. Later companionship and legendary
revelations remain future content; no encounter or capture route is added.
Save schema, map magic, runtime and font settings are unchanged. See
validation_lapras.md and Tests/rendered_lapras.rb for native Linux evidence.


### Glaciverm face refinement in 0.7.9

User requested Wurmple-like yellow eyes and a clearer omega-shaped snout.
Art/Glaciverm/mouth_detail.py now edits rounded yellow eye surrounds, dark
pupils, two rounded mouth lobes and a deeper transparent central notch.
export.sh also runs icon_detail.py to retain one yellow rim pixel lost during
icon reduction. Normal/shiny front sprites and both icon frames are rebuilt.
Rear view exposes neither detail and stays unchanged. No data, evolution,
encounter, map, quest or save changes; Lapras 0.7.8 is retained. Bible 1.16
remains current because this is a sprite refinement, with no new story canon.


### Authored Frostcoon in 0.7.10

This supersedes the provisional Silcoon stats/art/Shed Skin in 0.7.6.
Frostcoon remains FROSTCOON, Bug/Ice, form 0. Its native level-10 Cascoon PID
branch is unchanged. Stats in PBS order: 65/35/95/15/55/85, total 350.
Shell Armor is its sole ability. Full move schedule, tuning and dex entry:
Development/Art/Frostcoon/species_sheet.md and Bible section 27.

rebuild_glaciverm_data.py owns both branch definitions and matching PBS/metrics;
it now calls Art/Frostcoon/recolour.py instead of overwriting its art with stock
Silcoon. The manual palette recipe retains every source pixel and alpha value,
including both icon frames. Shiny shares the normal palette provisionally; cry
still inherits Silcoon. Ordinary Silcoon/Cascoon and Glaciverm are unchanged.

015_Frostcoon.rb refreshes previously owned provisional individuals after native
SaveData.load_all_values: party, storage boxes, astral souls and memorials.
It recalculates stats once, clears only obsolete cached Shed Skin, preserves
absolute current HP (including zero), status, PP, moves, item and identity.
The per-Pokemon revision makes the operation idempotent. No broad save reset,
forced move replacement, healing or resurrection. Other species are untouched.

No final dragon or forward evolution is registered yet, even at level 55.
Eviolite therefore has no evolution target to detect for Frostcoon in this
milestone; do not add a fake species to change that. Map magic, state schema,
Mac runtime and font settings remain. Tests/rendered_frostcoon.rb verifies native
PBS compilation, evolution, real old-data migration and battle rendering in a
disposable runtime. Do not embed test drivers in the release archive.


### Frostcoon support revision in 0.7.11

Supersedes only the 0.7.10 damaging learnset and its no-move-replacement policy.
All level-up and machine/tutor moves are now status category. Full schedule is
in Art/Frostcoon/species_sheet.md under Development and Bible section 27.
Spikes/Wish start its role at evolution; Stun Spore/Rain Dance arrive early;
Life Dew, Sticky Web, Sleep Powder, Hail/Aurora Veil and defensive tools follow.
Healing is battle-only HP restoration. Wish can heal a switched-in teammate;
Life Dew affects active allies, not the bench. No poison cure or resurrection.
Hail and hazards retain native indirect damage; no damaging attacks are granted.

015_Frostcoon.rb uses per-individual revision 2. Load migration covers party,
boxes, astral souls and memorials. It preserves status move choices/PP and
replaces damaging slots with unique level-appropriate support moves, carrying
at most the old PP. Existing HP/status/identity/items remain; revision 0 also
receives the earlier stats/obsolete Shed Skin refresh. Evolution normalizes
inherited Wurmple attacks after the native species setter. Standard level-0
Spikes and level-10 Wish learning then runs normally. No whole-save reset.

Tests/rendered_frostcoon_support.rb is the current native regression fixture;
rendered_frostcoon.rb documents historical 0.7.10 moves and is superseded for
moveset assertions. See Development/validation_frostcoon_support.md. Retain all
maps, art, runtime/font settings, branch conditions and reserved dragon work.


### Ice/Dragon final-evolution sprite milestone - 16 September 2026

Approved butterfly-dragon front artwork, matching rear view and two-frame party
icon are now installed as FROSTCOON_EVOLUTION (art identifier only). The original
approved design, rear source, reproducible export script and previews live in
Development/Art/FrostcoonEvolution. Battle canvases are 160x160; icon 128x64;
shared 16-colour palette, binary alpha and same-palette provisional shiny assets.
Gameplay remains 0.7.11. Name, species data, cry, final metrics and the playable
level-55 evolution remain pending; Frostcoon itself is unchanged. Do not invent
those decisions merely because sprite assets now exist.


### Nivalora: playable final evolution in 0.7.12

Supersedes the earlier reserved/art-only status. Working name Nivalora; species
NIVALORA, Ice/Dragon, form 0, Frostcoon -> Level 55 -> Nivalora. The existing
Wurmple personality split and Glaciverm remain. Stats in PBS order:
100/45/65/145/130/115, total 600. Sole ability Shield Dust, no hidden ability.
All implemented details are in Art/FrostcoonEvolution/species_sheet.md under
Development and Bible section 28. No poisoning move compatibility; Frostcoon
still has a status-only moveset. Evolution retains existing moves and offers
Dragon Breath, plus Ice Beam at 55. Delayed evolution follows native rules.

rebuild_glaciverm_data.py calls rebuild_nivalora_data.py last, maintaining the
forward/reverse evolution data, native PBS, sprite metrics, art aliases and cry.
Art/FrostcoonEvolution/export.py also updates registered NIVALORA sprites when
its PBS exists. Preserve the approved front and corrected rear silhouette.
Same-palette shiny art and reused Articuno cry are declared placeholders.

Growth stays Medium across this regional Wurmple line: the user's requirement
is the 600 stat total, not a retroactive Slow-growth conversion. No saved level
or experience rewrite. No new runtime hook or save reset; native evolution
preserves the individual. Existing over-level Frostcoon qualify on their next
level-up. Frostcoon now naturally qualifies for Eviolite. No new encounter table.

Tests/rendered_nivalora.rb verifies native PBS, evolution boundary/Everstone,
identity, saves/storage/astral, images and battle behavior. Earlier test fixtures
asserting no final evolution describe prior milestones and are superseded.


### 0.7.13 evolution-testing supply

User requested 99 Rare Candies at game start to test evolutions. Added once to
$bag in Opening.begin_story, below its existing opening_started guard. New games
only; no load migration, replenishment, debug mode or changes to item mechanics.
Continue preserves current quantities. Remove the grant in a future production
balance pass only when authorized. All 0.7.12 species data/art are unchanged.
Bible 1.19 remains current; this is a testing convenience, not new lore.


### 0.7.14: natural landscape pass

`Development/landscape.py` runs after shoreline generation in rebuild_maps.py.
It changes maps 102, 103, 108 and 112 only; original event IDs and coordinates stay
stable. Native trees form varied groves and an enclosing forest canopy, with
clearings for keys, encounters, fires and the pool. The headland's boulders have
rubble skirts and offshore skerries. Small planted beds flank the lighthouse;
the south road and dock courts have their own restrained planting.

Native art is composited into `Graphics/Tilesets/TideboundLandscape.png`, using a
cloned tileset (currently 26), three animated water palettes and generated solid
masks. Original Outside.png and its tileset are untouched. Native rows through
451 remain at their original IDs, preserving glass-only window lighting; the
custom atlas starts after row 455 and must remain below 16,384 pixels tall for
Mac GPU compatibility. No imagery generation or runtime dependency was added.

Keep scripted walk corridors and event approach buffers clear. All 180 existing
events, arrival points, fire/berry access and vast ocean camera margins are
validated by validate_maps.py. Tall grass retains native encounter terrain.

016_Landscape.rb adds per-map `story[:landscape_revisions]` (revision 1). When
loading/entering an affected map for the first time, an invalid old position is
moved to the closest unoccupied tile in its primary connected region, excluding
touch triggers. Only Tidebound's Pookie follower is eligible for repositioning.
No story schema bump, map magic change, save reset or quest replay. Keep this
migration additive when extending it. Bible 1.19 is unchanged; no new lore.

See Tests/rendered_landscape.rb and validation_landscape.md. The native Linux
engine was used for visual/integration checks; a native Mac playtest is not
possible in this environment. Mac bundle 0.7.14/build 23 retains the same engine,
fontHeightReporting=1 and save directory. 99 Rare Candies remain new-game only.


### 0.7.15 — dense boundaries and transition alignment

The user's clarified map direction: early-generation density, with paths and
clearings carved out of broad continuous tree/rock masses. Avoid scattered
isolated decoration and extensive unused grass. Preserve the darker perpetual
night palette, the sheltered lighthouse garden and large open ocean at the pier.
Reference comparison: Petalburg Woods and FireRed Viridian Forest map layouts;
no reference assets were imported.

landscape.py now fills grove areas with overlapping native crowns and uses
explicit clearings for encounters, berries and story interactions. Complete
32px small-rock sprites are extracted from the full native 64px cells before
composition; the former one-tile fragments were only half the object. Large
boulders use their complete native 96px artwork. Scree regions form substantial
boundary piles. Preserve path and event buffers when editing these regions.

010_FieldDetails.rb anchors all 22 TideboundThreshold cues directly to map-tile
coordinates. The lighthouse transfer is on the approach tile below its facade:
its marker must use that tile's TOP edge (y+1), not the old character-foot offset.
Forest/north-route thresholds also use the upper edge; the dock-city exit points
east; the return from the docks points west; facade and southern exits use the bottom edge. A small dedicated viewport
keeps cues visible above ground tiles; it is disposed with its sprite.

016_Landscape.rb revision 2 extends the existing per-map safe-position migration
to 0.7.14 saves. All original event IDs, transfers and quest scripts remain.
Native validation and screenshots: validation_density.md and
Tests/RenderedEvidence_0_7_15. Mac 0.7.15/build 24; Bible remains 1.19.


### 0.7.16 — lighthouse interior refinement

`Development/lighthouse_interiors.py` runs after landscape.py inside the map
builder. Maps 101, 104, 107, 110 and 111 use the cloned Tidebound Lighthouse
tileset (27); its atlas includes complete native furniture and stairs, muted
wood/plaster upstairs, dressed stone below, night windows and a new beacon.
The original Interior general.png remains intact. Exact object crops must not
include adjoining props. Rebuild maps and scripts after layout edits.

All 180 events retain their IDs, coordinates and commands. Preserve the bedroom
Mother route, hall Maku/crate movements, dinner table at (8,7), meal actors, and
Mother's route along row 7 then column 3 to the cellar. Stairs have complete
2x3 art with the original trigger on the lowest tread. The cellar still unlocks
through the necklace follow-up; decorating it does not unlock it early.

017_Lighthouse.rb draws only the lit lens over the static beacon. The existing
Main lamp event and lamp_lit flag remain authoritative; the generic small lamp
sprite is suppressed on map 104 only. The unexplained downward lamp is unchanged.
No mythology, new quest or unexplained symbols are added to the vault.

016_Landscape.rb adds the five interior map anchors to existing per-map save
recovery. No schema change, item grant, party reset or outdoor migration reset.
Save directory and fontHeightReporting=1 remain. New games retain 99 Rare Candies.
Mac 0.7.16/build 25; Bible 1.19 unchanged. Native Linux validation and screenshots:
Development/validation_interiors.md and Tests/RenderedEvidence_0_7_16.


### 0.7.17 — one-time psychic bedroom maze

Confirmed: the giant bedroom maze is Natu's projection; its cause is explained
later. The first iteration is deliberately small. Find Natu, hear Mother's
call, return to normal room 107, then continue the existing hall scene.
No encounters, starter grant, costs or permanent failure. Existing saves skip it.

New map 114, Your Room, starts at (5,20). psychic_maze.py runs inside
lighthouse_interiors.py before atlas serialization. It extends that tileset
without moving existing tiles and generates coordinate constants in
018_PsychicMaze.rb. The controller handles bounded directional slides, off-pad
teleport landings and once-only completion. The opaque black background hides
the native engine's below-floor reflections outside the puzzle platforms.

004_Opening.rb sets :psychic_maze=>:active only in first initialization on map
114. Completion sets :complete and bedroom_talk before returning to 107.
Completed/legacy entry to 114 is rejected. Never infer newness from an empty
party. Natu's identity persists. No save schema/magic-number change; the same
once-only initialization grants 99 Rare Candies to new games.

All 13 existing maps and 180 events remain byte-identical; map 114 adds 15
events. validate_maps.py includes directed warp edges. Tests/maze_graph.py
resolves forced movement and proves each reachable resting position can reach
Natu. rendered_maze.rb tests new, resumed, completed and legacy journeys.

Bible 1.20; guide 2.17; Mac 0.7.17/build 26. See validation_maze.md and
Tests/RenderedEvidence_0_7_17. Linux engine checks do not replace Mac playtesting.


### 0.7.18 — false bedroom prologue

New map 115 starts at (7,8). Both stair treads loop to the centre. All furnishings are inspectable; the computer is a custom message menu, not the storage PC. dream_room.py appends art and map data after psychic_maze.py inside lighthouse_interiors.py. Existing maps and tile indices remain stable.

019_DreamRoom.rb owns the sequence. Opening.flags[:dream_room] holds phase (:sealed, :wick, :complete), streak, riddles_solved, door_loops, last_sleep. Initialization occurs only on a fresh map-115 opening. Do not backfill this state onto older saves. Riddle answers are Thursday / The empty chair / Under the pillow. A wrong answer or cancelling an unfinished run resets the streak; all three correct unlock the persistent sleep menu. Only duration index 6 (12 years) reveals Wick. This is a brief dream transition, not a real-time wait or canonical calendar jump. Presentation fades the existing household Natu actor in; no Pokemon is added or replaced.

Wick sends the player to 114, marks the dream complete and activates the established maze controller. Completed or legacy journeys redirected into 115 are sent back to the normal bedroom (or the active maze). Never replay the dream on Continue. The save namespace stays Tidebound_Opening_0_2.

Bible 1.21; guide 2.18; Mac 0.7.18/build 27. New Game is needed to see the prologue. Tests/rendered_dream.rb is a disposable test fixture, never an embedded game script. See validation_dream.md and Tests/RenderedEvidence_0_7_18. Linux engine validation does not replace Mac playtesting.


### 0.7.19 — second false bedroom and period direction

Map 115 replaces the CRT with a book cupboard without moving its footprint or event IDs. Its current interaction is cupboard; the computer method remains an old-command compatibility alias only. inspect_object(:shelf) offers a backwards book, then Water curse. The optional four-page full-screen reading is authored nonsense, never reliable late-lore exposition. Its viewport, bitmaps and sprites are disposed on all exit paths. Confirm advances; Cancel closes. The text displacement uses low-contrast drifting strips, no strobe.

019_DreamRoom.rb now adds phase :folded and map 116. Existing :sealed/:wick saves continue normally; :complete or absent state never starts a new dream. Wick transfers from 115 to 116; four correct answers finish it and activate the existing 114 maze. folded_streak resets on any wrong/cancelled answer; folded_resets counts returns to (7,22). Completion does not restart room 115.

folded_room.py runs after dream_room.py inside lighthouse_interiors.py. It appends isolated recoloured/fractured tile copies, full-width bookcases, three clear gaps and four clue books. Do not change the original 101-114 map geometry. Map 116 bed approach is (25,7); staged player position is (24,5). First-room bed position is (3,5), safe return (4,7). on_bed ensures actors are never left stranded on a solid bed after a cancelled prompt. fold_to restores opacity and facing even if interrupted by an exception.

A Game.load_map prepend refreshes only map 115's cached geometry/events on load, replacing old CRT tiles. It does not change map magic, save schema, companion identities, quest state or other map events. No migration inserts missing dream state into an established journey. Native test fixture rendered_folded.rb is disposable, never embedded.

Bible 1.22; guide 2.19; Mac 0.7.19/build 28. See validation_folded.md and Tests/RenderedEvidence_0_7_19. New Game is required for the complete revised opening. The Linux native engine can check game behavior; Mac execution remains the user's playtest.


### 0.7.20 — Natu's playable dark prelude

020_BirdPrelude.rb prepends Game.start_new only. After the native new-game initialization, it temporarily replaces the pending Scene_Map with Scene_TideboundBirdPrelude; completion restores that exact map scene. It never wraps Game.load or changes the starting map, character graphics, party, inventory, switches or save schema. The normal room autorun performs Opening.begin_story afterward. :bird_prelude_seen is a completion marker, not a Continue gate.

The prelude uses a small fixed path graph, four-way native input, eased tile movement, bounded collision, optional blind branches and automatic completion at the bedside. It offers no inventory/save menu during its brief duration. Continue uses the normal map loader and bypasses the scene regardless of flags. No new Pokemon instance or rerolled household identity is created by this display.

Artwork uses native Natu icon, bed and protagonist head crops. The sleeping eyelid and breathing are in-memory animation layers; original PNGs remain intact. Runtime bitmaps draw faint paths, Gaussian mist wisps and text. Assets and scene objects are disposed in ensure. The existing Stillness loop plays at volume 25/pitch 80; map autoplay restores the normal atmosphere after completion. There are no new maps or external runtime dependencies.

The scene orders sleep, eye opening, the exact caption A bird wants to play., movement, bedside pause and fade into the first room. Do not explain the dream's relationship to later astral lore. All previous opening rooms and puzzles remain intact. Bible 1.23; guide 2.20; Mac 0.7.20/build 29. Native test: Tests/rendered_bird_prelude.rb. Evidence: validation_bird_prelude.md and Tests/RenderedEvidence_0_7_20. Linux engine tests are not Mac playtests.

### 0.7.21 — music balance

The two Tidebound ambient loops keep their original arrangement but have a linear master gain: Shore 2.0×, Stillness 2.5×. New map/title Shore and map Stillness requests are level 80; the bird prelude is level 65 at its original pitch 80. Development/021_AudioMix.rb intercepts only those two named tracks at Game_System playback: it maps old saved-map volume 45 to 80, old prelude 25/pitch 80 to 65, and caps battles and victory requests at 80. Game_System then applies the player music-volume setting as before. Other music, sound effects, maps and saved quest variables are unaffected. Native Mac listening remains an on-device check. Validation: Development/validation_audio_mix.md. Mac build 30.

### 0.7.22 — Tidebound Psyduck and Whyduck

Regional wild Psyduck on southern road Map 108 (10% of Land encounters, levels 4–6) receives form 1 via 014_RegionalForms.rb. It gains Water/Psychic typing without changing its existing level-up moves, appearance, stats or cry. Existing owned ordinary Psyduck and Golduck stay ordinary. Psyduck form 1 evolves at level 33 into the original Whyduck species (form 0 via DefaultForm_0). Whyduck's sprite is hand-drawn from the original Psyduck silhouette on a 2x pixel grid in Development/Art/Whyduck/draw_sprites.py: front/back, their shiny variants and a two-frame icon. Its psychic crown is blue/violet; calm eyes distinguish it from the parent. The cry currently reuses the Psyduck cry as a declared placeholder.

Whyduck's stats in engine order are HP 75, Attack 55, Defense 70, Speed 75, Special Attack 130, Special Defense 115 (BST 520). It has Own Tempo or Cloud Nine (hidden Inner Focus). Evolution move Psychic and later Psyshock, Future Sight, Psychic Terrain, Recover and Stored Power support a resilient special attacker. Source: rebuild_whyduck_data.py (also called at the end of rebuild_regional_data.py). rebuild_field_data.py recompiles the road roster. Keep PBS pokemon_forms_tidebound_psyduck.txt, pokemon_whyduck.txt, pokemon_metrics_whyduck.txt and encounters_tidebound.txt aligned with compiled Data. Bible 1.24 section 29 records its unresolved origin. Validation: Development/validation_whyduck.md. Mac 0.7.22/build 31.

### 0.7.23 — Whyduck visual redesign

Creative direction: the supplied penguin-like image replaces the earlier almond-shaped blue crown and hands-near-head silhouette. Development/Art/Whyduck/draw_sprites.py now authors all five WHYDUCK sprite files at native 2x pixel resolution. Normal: cream-yellow Psyduck-like duck body, forward-facing level eyes, outstretched arms, and a broad light-green exposed brain with two uneven, deeply folded hemispheres. The skull has a visible broken bone lip, shaded gap and short green roots; the organ is integral to the head rather than a decorative object. Rear view shows the same opening, brain and outstretched arms. Shiny counterpart has violet folds and pale blue body. The icon has both animation frames. Source is run automatically by rebuild_whyduck_data.py. Whyduck sprite metrics were adjusted for the larger artwork (front [1,13], back [0,5]); Pokémon stats, moves, encounter chances, cry and save schema stay as in 0.7.22. The source image supplied by the user is a visual reference, not a game asset. Bible 1.25 revises the design; the origin of Whyduck's brain remains open. Tests: Development/validation_whyduck_visual.md. Mac 0.7.23/build 32.

### 0.7.24 - approved Whyduck sprites

Approved draft 09 is implemented. Development/Art/Whyduck/draw_sprites.py plus pieces/ reproduce front, back, shiny and both icon frames. The yellow body has Psyduck-like orange flanks and a pink exposed brain. Its eyes and bill reuse the native Psyduck pixels with only the pupils moved down-left; the casting hands reuse and rotate Psyduck hand pixels. Rear view reverses the raised arm. Shiny is blue-bodied with a green brain. To regenerate eye cutouts run make_eyes.py before draw_sprites.py; compare_psyduck.py renders a side-by-side. Evolution, stats, maps, saves and cry unchanged. Bible 1.26 section 29; Mac 0.7.24/build 33.


## Demo 1 / 0.8.0 — 23 September 2026

The opening caption now adds “Take it for a little walk, 100 steps.” This is wording only: guide Natu to the bed as before; no step counter was added. Pokémon losing their HP are described as having died, including field poison, while the existing battle and astral mechanics are retained.

Shiohama's three cottages use salt-weathered dark timber and stone footings. Window glass and its warm light stay aligned. The lighthouse artwork is unchanged. South Coast Road has a visible level-8 Tidebound Psyduck near the shallows, in addition to its existing rare grass encounter. Regional Psyduck now evolves into Whyduck at level 16; an older regional duck above 16 evolves at its next level-up. Ordinary Psyduck still evolves into Golduck at 33.

The docks now have two wooden sailing ships, sixteen new sailors including a captain, cargo stacks, a sailing notice, a ledger and a modest memorial. Nell (Wingull 8, Wooper 9) and Oren (Poliwag 10, Krabby 11) offer optional battles and remember a win. These use the existing astral-loss flow; neither is required for the story. Other sailors discuss trade, letters, watches, mountain settlements and everyday coastal life without explaining the late mythology.

Speak to the captain at the end of the eastern pier about **Psyduck Island**. Accepting reaches the demo's ending message. You remain in the docks and can continue exploring and saving. The island and voyage gameplay are future content.

Continue preserves existing party, inventory and quest flags. Updated map data reloads on old saves; a player standing where a new dock actor was placed is moved to a nearby clear tile. New Game is required to see the opening caption. The previous 99 starting Rare Candies remain available for evolution testing; this release does not remove user-requested supplies. Keep a backup before overwriting a save with a new journey.

### Demo implementation and rebuild

`022_DemoLaunch.rb` owns the additive `Opening.flags[:demo_launch]` hash, sailor dialogue/battles, ending and map-position recovery. `NeighborQuest.q[:shoreduck_gone]` integrates with the existing overworld companion renderer. Winning or capturing removes this fixed encounter; running or losing leaves it available. Optional sailor wins persist; loss/cancellation never marks a win. There is no new game-state schema or quest prerequisite.

`demo_maps.py` runs after landscape/interior generation, appends event IDs, adds the map-108 Psyduck and map-112 crew/props, and assigns map 102 a cloned TideboundVillage atlas. `demo_art.py` draws the two sailing vessels/cargo on a 2x pixel grid and recolours only cottage tiles. Lighthouse rows and glass pixels are preserved. The dock ship props are visual only; mooring interactions remain on reachable pier tiles. Stock skiffs are retained and shifted out of the hulls.

`rebuild_scripts.py` replaces the exact visible faint messages in stock Battler_ChangeSelf and Overworld while preserving mechanics and method names. It embeds the numbered source files once. `rebuild_whyduck_data.py` maintains level16 forward/reverse evolution plus PBS. Do not change ordinary Psyduck's level33 evolution. Map magic 26092301 reloads event data for old saves. Save directory remains Tidebound_Opening_0_2. Mac version0.8.0/build34, same native runtime.

Run rebuild_maps.py, rebuild_whyduck_data.py, rebuild_scripts.py and validate_maps.py with rubymarshal/Pillow installed. Tests/demo_native.rb is a disposable native test driver, not release code. See validation_demo_080.md for completed checks and platform limits. Later content, including Psyduck Island and the museum heist, remains unimplemented.


## 0.8.1 — regional Ekans / Arbok (24 September 2026)

`rebuild_snake_data.py` creates form 1 of both species, Normal/Dark, and replaces
all Poison moves across level-up, tutor and egg pools (including Coil). Run it
independently or via `rebuild_regional_data.py`, then `rebuild_scripts.py`.
`Art/Snakes/recolour.py` regenerates matching front/back/shiny/icon PNGs by exact
palette substitution from unmodified ordinary assets. Stats, abilities, cries,
metrics and native level-22 evolution stay unchanged; gray shiny art is provisional.
`014_RegionalForms.rb` selects form 1 for new map-108 Ekans/Arbok and resets their
initial moves. It does not migrate already-owned ordinary snakes or add Arbok to
encounter tables. Native evolution retains form 1; never add DefaultForm_0 here.
`Tests/regional_snakes.cjs` uses actual Essentials objects for encounter hooks,
learnsets, evolution, ordinary-form isolation and save preservation. Run after
Tests/prepare_reference.py and npm ci. Packaged in 0.8.1 (Mac bundle build 35); release 0.8.0 ZIPs remain unchanged.


## 0.8.2 — inhabited hideout and The Mending

`hideout_room.py` runs inside `lighthouse_interiors.py` before the shared atlas is saved. It rebuilds only map109, retains event IDs/arrival11,14 and adds two sofa-approach touch triggers. Its rubbish banks create a west/east zigzag. Furniture, blocking heaps and walkable scattered wrappers must remain visually distinct. The console is wooden/rune-powered; no general electronics retcon. Ivo uses a seated native Camper derivative until his battle.

`023_Hideout.rb` owns the new sequence and routes old runner/second_thief/overhear callers into it. Existing neighbor quest stages and runner_won/second_won flags remain authoritative. The added hideout_game_won flag skips the minigame after subsequent trainer loss. hideout_revision=1 places a legacy map109 player on the clear entrance once. Map magic26092501 refreshes cached maps. An already defeated legacy boss skips the new game and keeps the earned reward. Only successful bag collection advances to necklace; the cupboard remains a retry point. No save-schema or save-directory change.

Guard wins and boss wins use the existing trainer!/astral adapter. Declining, canceling or losing cannot advance either victory. An unsuccessful approach restores the player to the near side of the guard line, unless the loss transferred them to the astral map. Ivo stands for battle, walks to the cupboard on victory and restores normal collision after his short route. Completed saves position him by the cupboard. Existing rosters and all other quest beats remain.

The Mending is a synchronous, isolated native Sprite/Bitmap/Input scene, never a second installed plugin or browser app. Three reachable nests, persistent progress after contractions, a locked northern exit and free cancellation keep it modest in difficulty. It never mutates real Pokemon or inventory. Every sprite, bitmap and viewport is disposed in ensure; map music resumes on return. Rendered pixels are generated by the Ruby scene; no external art model or new dependency.

Rebuild maps, scripts, and validate_maps.py. Run Tests/native_domain.cjs (includes hideout_flow.rb) for native-object saves, guard/minigame/boss gates, full-bag retries and pure minigame rules. Tests/hideout_native.rb is a TEST-ONLY disposable Linux engine driver for actual graphics, input and two battles; never embed it in release Data. Refer to validation_hideout.md for completed evidence and platform limits. Bible1.29 section31 records confirmed direction versus prototype choices.

## 0.8.3 — neglected squat atmosphere

hideout_room.py replaces map109's domestic furnishings with code-drawn pallet mattresses, broken crates/locker, torn sofa, battered wash trough and improvised bench. Windows are boarded; no household lamp or neat rug remains. Floorboards and limewash are damp and cracked. The final palette pass clones tiles instead of recolouring shared entries, protecting every lighthouse room. 004_Opening.rb gives map109 a dedicated Tone(-35,-32,-25,95). Collision masks and event positions are unchanged. Map magic26092502 refreshes existing saves. Mac build37. Native screenshots and focused validation are in HideoutEvidence_083 and validation_hideout_atmosphere.md. No new lore or quest changes.

## 0.8.4 — southern pond, 26 September 2026

Map108 now has a substantial pond clearing. The existing level8 Psyduck moves to19,62 and retains shoreduck_gone. Local pond grass: Psyduck40% level8-11, regional Sunkern35% level8-10, Aipom25% level8-11. Northern road encounters are unchanged. Three optional fishermen remember victories and use the existing astral-loss adapter: Toma (Magikarp9/Goldeen10), Ida (Wooper10/Poliwag11), Renzo (Barboach12). An Oran tree uses existing two-berry regrowth. The hidden western path ends in a one-time Mystic Water with full-bag retry.

The central obelisk requires later Surf. Pond water has StillWater terrain and player-only Surf passage; no HM or badge is awarded. Its origin, inscription, purpose and future reward remain open. Older saves on new obstacles/water/islet move once to26,52. Map magic26092503; Mac0.8.4/build38; same runtime, font fix and save identity.

pond_map.py runs after demo_maps.py and generates024_PondGeometry.rb plus a compact road-only atlas. 025_Pond.rb handles pond encounters, optional battles, item and migration. Grass tile391 is preserved. Tests/pond_geometry.py verifies the island is unreachable on foot and reachable with Surf; validate_maps.py explicitly excludes the future-Surf obelisk. All other15 maps remain unchanged. The recovery recipe is now historical; do not apply it again. See Development/validation_pond.md.


## On-demand CI verification

PR/main pushes run quick Linux checks. Before merging a change, request full
verification with an exact `/verify` PR comment (repository write permission
required) or Actions > Requested verification > PR number. The green Full
verification status must match the current PR head; new commits need a new run.
Release tags always run the complete matrix. See Development/RELEASING.md.

## 0.8.5 — verified Mac and Windows packaging

Post-release packaging correction: Archive Utility normalizes Unicode filenames,
which broke the 0.8.5 signature for `Routé 1.mid`. Normalize staged Mac bundle
names to NFD before signing, preserve asset bytes, and check the extracted app's
original signature after the same normalization. Do not treat direct native
execution as a Gatekeeper/notarization test. See Development/RELEASING.md.

This release changes packaging and developer workflows only. Mac build39 is
universal Intel/Apple Silicon; the Windows x64 player ZIP retains the existing
executable and DLLs. Native CI covers boot, compiled data, Pokemon/state disk
persistence and rendering on all three platforms. Hosted Windows uses CI-only
Mesa software graphics and silent OpenAL; real audio/GPU behavior and Monterey
playtesting remain manual. Release tags prepare drafts after all gates pass.

The only embedded game-source changes from 0.8.4 are the displayed version in
Settings and `Tidebound::VERSION`. Preserve all maps/assets, event IDs, quest and
save schemas, and the `Tidebound_Opening_0_2` save directory. Bible1.30 is unchanged.
