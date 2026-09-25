# Tidebound — The Keeper's Light

Demo 1 **0.8.2** · Pokémon Essentials **21.1**

## Demo 1 / 0.8.0 — 23 September 2026

The opening caption now adds “Take it for a little walk, 100 steps.” This is wording only: guide Natu to the bed as before; no step counter was added. Pokémon losing their HP are described as having died, including field poison, while the existing battle and astral mechanics are retained.

Shiohama's three cottages use salt-weathered dark timber and stone footings. Window glass and its warm light stay aligned. The lighthouse artwork is unchanged. South Coast Road has a visible level-8 Tidebound Psyduck near the shallows, in addition to its existing rare grass encounter. Regional Psyduck now evolves into Whyduck at level 16; an older regional duck above 16 evolves at its next level-up. Ordinary Psyduck still evolves into Golduck at 33.

The docks now have two wooden sailing ships, sixteen new sailors including a captain, cargo stacks, a sailing notice, a ledger and a modest memorial. Nell (Wingull 8, Wooper 9) and Oren (Poliwag 10, Krabby 11) offer optional battles and remember a win. These use the existing astral-loss flow; neither is required for the story. Other sailors discuss trade, letters, watches, mountain settlements and everyday coastal life without explaining the late mythology.

Speak to the captain at the end of the eastern pier about **Psyduck Island**. Accepting reaches the demo's ending message. You remain in the docks and can continue exploring and saving. The island and voyage gameplay are future content.

Continue preserves existing party, inventory and quest flags. Updated map data reloads on old saves; a player standing where a new dock actor was placed is moved to a nearby clear tile. New Game is required to see the opening caption. The previous 99 starting Rare Candies remain available for evolution testing; this release does not remove user-requested supplies. Keep a backup before overwriting a save with a new journey.


A quiet lighthouse home, a village errand, a shape beneath the pier, and a forest
where losing a battle can lead somewhere other than home.

## Start

Mac: unzip Tidebound_Mac_0.8.2.zip, move Tidebound.app to Applications and
Control-click > Open for its first launch. See MAC_README.txt if Monterey asks
for an Open Anyway action. No Codex, Wine or Windows installation is needed.

Windows: unzip the maintained project and open Game.exe inside Tidebound_Prototype.
Keep its Data, Audio, Graphics, Fonts and runtime files together.

Press Return, then New Game. The Mac app includes its game files internally.
The editable project and game bible are in Tidebound_Project_0.8.2.zip.

Use the arrow keys to move and **Enter** to interact. **Esc** opens the menu or
backs out. Use **F1** to view or change the launcher's key bindings. Save from
the menu. This build uses its own save folder, separate from the Essentials demo.

## A first walk

- Find Wick in the bedroom maze. Mother's call returns you to the small room; go downstairs.
- After her talk, find Pookie asleep just outside the lighthouse and speak to her.
- Walk 100 steps around the village. Near the pier she may run away; speak to
  her at its end to resume following. You can also skip the pier entirely.
- Return home together after 100 steps. Choose Wick the Natu, Maku the Makuhita
  or Pookie the Poochyena. Mother then asks for lamp oil.
- Speak to the seller beside the locked shop. Find his keys among the white
  flowers in the northern forest, then bring them back to him.
- He goes inside. Enter the shop for the oil; bring it home and tend the great
  lamp upstairs. A later pier visit offers another glimpse of the shore's mystery.
- The seller also gives you pie. Speak to Mother to eat it together, then return
  the washed plate to his shop. A robbery sends you after two boys down the
  south coast road, reached from the southern edge of the beach.
- Find the first thief, then follow the second to the old storehouse. Listen,
  face its runner and recover the necklace. Bring it back to the seller.
- A travelling ninja on the road offers **Rest** before the storehouse. The
  northern forest fire also remains available; both set a return checkpoint.

The notebook records your current errand and lets you rename Ren. The forest's
pool is dangerous; no battle is required to retrieve the keys. Makuhita can use
Foresight before Normal/Fighting attacks against a Ghost.

Existing 0.2–0.5.1 saves keep companions and progress, without another starter.
If your oil errand is already complete, speak to the seller inside for the pie.
Choose New Game to see the earlier prologue; back up your old save before saving
that new journey over it.

## Try the astral sequence

The pool in the eastern forest contains a stronger Frillish. If it defeats your
whole party, you wake beyond the shore. For an intentional test, use non-damaging
moves and allow that battle to be lost.

A borrowed Natu lets you fight there. Search for the visible, wandering forms of
your actual fallen companions. Each has one encounter and a six-turn deadline.
Catch one to recover the original individual, including its nickname, owner,
moves, IVs and held item. Fainting the spirit, losing or fleeing its battle, or
running out of turns loses that companion. The warning appears before you begin.

Leaving also loses any spirits still waiting; the exit asks you first. A small
memorial records losses. With no survivors, a different Natu accompanies your
return so the save can continue. The borrowed guide cannot leave the astral map.

Each fire restores full HP and PP once every 15 real minutes. Cooldowns are
independent and saved. Rest does not cure poison or other status conditions.
Five berry trees provide two Oran or Sitrus Berries each and regrow in one hour.
Tall grass contains Aipom, Weedle and regional Wurmple in the forest, or coastal Zigzagoon, Sunkern and Ekans;
ordinary paths remain safe from random encounters. There are no Centres or healing shops on
these maps. Ordinary manual saves are supported; loading an older save can still
roll back losses. An enforced autosave policy is not part of this prototype.

## What this version contains

Thirteen native story maps (101–113), bedroom/family scenes, Pookie's walk, forest keys, oil/lamp quest, household choice, a later Lapras glimpse, four
visible optional wild encounters, additional tall-grass encounters, timed fire resting, the astral search and recovery loop,
loss records, a title screen and two original ambient audio loops. Source code,
rebuild scripts and the longer design record are in **Development**.

The kit's existing art is temporary. Lapras uses a pale stock icon here; its
custom Water/Ghost form and final sprite are not implemented. The regional dex,
Koga arc, shrines, Dive progression, Suicune and endings remain future chapters.
The death wrapper currently applies to the explicit opening battle events;
future battles must use the wrapper too. Individual battle faints become astral
loss candidates when the whole party is defeated.

## Validation and limits

Code, native-object save tests, all starter choices, migration and map checks
pass. The updated opening also rendered in the actual Linux engine with scripted
inputs and full engine saves. See Development/validation_report.md for scope.
The Mac bundle's Intel deployment targets and dependency paths were inspected.
The user has played the preceding Mac build and reported the doorway and light
issues fixed in 0.7.1. This update still needs their on-device check; the agent
cannot run macOS here.
Keep the exact error text and save if something fails.

The original Essentials assets, attribution and credits remain included. This
is an unofficial fan project. Tidebound, Ren, Wick and the place names are
working names.

0.7.0: After returning the necklace, collect the seller's keepsake, follow him
to the lighthouse and speak to Mother. Take the hall stairs down to the vault.
After their conversation, take the east path beside the old storehouse to the
docks. Enter the museum and inspect the sabre. Existing completed-quest saves
start this chapter by speaking to the seller in his shop.

0.7.1 fixes immediate hideout/lighthouse entry after the departure scenes and
aligns warm highlights to the window glass. Explore the dock city's new paved
lanes, houses, waterfront workshops, boats and quay details. The added shop
frontages are closed; the existing museum interior remains open. Continue your
existing save. No new story chapter or museum heist is included in this update.

0.7.2 introduces Tidebound Sunkern, a Grass/Dark regional form weakened by the
absence of sunlight. New Sunkern encounters in the South Coast Road grass use
this form. It has wilted leaves, muted colours and sad eyes, with matching
front/back sprites and party icon. At local encounter levels it knows Absorb,
Growth and Payback. Previously caught Sunkern keep their existing form.

0.7.3: Tidebound Sunkern now evolves into Moonkern at level 24. Moonkern is a
Grass/Ghost with a hollow spectral body, much stronger special stats and Hex
on evolution. This replaces the regional form's provisional Sun Stone path.
Ordinary Sunkern still evolves into Sunflora with a Sun Stone. A regional
Sunkern already above level 24 can evolve at its next level-up.

0.7.4 supersedes the level-24 rule: Tidebound Sunkern evolves into Moonkern at
14, then Moonflora at 20. Moonflora is Grass/Ghost and learns Shadow Ball upon
evolution. Its art uses a simple Sunflora silhouette, flat muted colours, a
hollow face and weary expression. Existing companions qualify at their next
level gain; no new game or forced transformation.


0.7.6: regional Wurmple now evolves at level 10 into Glaciverm or the provisional
Frostcoon, based on its fixed personality value (roughly equal odds). Glaciverm
is a fully evolved Ice/Bug with Technician, strong physical stats and priority
moves. Existing regional Wurmple above 10 qualify at the next level-up. Ordinary
Wurmple stays unchanged. Frostcoon's level-55 Ice/Dragon remains future work.


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


## Revised hideout

During the necklace pursuit, enter the old storehouse on the south road. Follow the gaps through the rubbish and approach the sofa. Defeat Bram, speak to Ivo, and accept his game. Arrows move; Enter loosens a nearby stitch; Escape leaves. Free all three nests, then reach the northern mouth. Contractions preserve released nests. After winning, defeat Ivo in a Pokemon battle and receive the necklace by the cupboard. The minigame never affects your actual party. Existing finished quests remain finished; start a separate new journey if you want to replay that story.
