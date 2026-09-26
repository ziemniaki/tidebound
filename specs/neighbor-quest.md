# The neighbour's plate — 0.6 content and maintenance

The playable objective is small: help the oil seller recover his wife's necklace.
The warm meal is sincere; the early thieves are funny. No one explains late lore.

## Editable sources and events

- 008_NeighborQuest.rb: stage transitions, dialogue, NPC rosters and quest methods.
- 009_NeighborPresentation.rb: meal plate/pie and local pearl glint.
- 002_Essentials.rb: shared living-battle wrapper, now including TrainerBattle.
- 004_Opening.rb: journal hint and fixed-night registration for maps108/109.
- 005_Presentation.rb: correct species and independent disappearance for road wilds.
- rebuild_maps.py: the authoritative map/event source. Do not edit generated maps
  independently without bringing their source and passage masks back into agreement.
- rebuild_neighbor_data.py: real Key Items, trainer types, PBS and reference icons.

Map101 Mother calls the short meal after oil delivery; household individuals remain
unchanged. Map106 Oil seller offers pie or accepts the recovered necklace. Map102
Shop door starts the robbery before transfer; new hidden youth actors run south.
Its small southern path leads to108. The original sixteen coast event IDs are kept.
Map108 contains the first thief and three crossing triggers, two optional wilds,
the second thief's storehouse approach/door and limited rest. Map109's arrival
runs the overheard scene; runner and necklace thief are the two further battles.
The packer/lookout and mismatched crates establish ordinary theft and distribution.

## State

`story[:neighbor_quest][:stage]`: nil, pie, plate, pursuit, necklace, complete.
Separate first_won, hideout_seen, heard, runner_won, second_won and two wild-gone
flags survive saves. No new global switches; native battle outcome variable1 is
unchanged. Only outcome1 wins a trainer fight; loss/draw follow the astral route.
An unsuccessful item addition cannot advance the item handoff. A won final battle
stays won even if the bag is full; speak again to collect the necklace.

Legacy oil-complete saves receive a belated pie inside the shop. Existing oil,
lamp, starter, household, coastline, checkpoint and memorial state is retained.
Schema1/opening4/coast5 persist. Map magic26091006 reloads map/event definitions.
The same save directory and native Mac runtime remain configured.

## Implementation choices and limits

Ellie is a working mother name; Toma/Ivo/Bram are provisional thief/runner names.
The boys are coastal visitors, preserving the elderly resident population.
The two-reed plate design is ordinary ceramics. Its bag icon is a stock Shoal
Shell placeholder; the meal uses a custom code-drawn plate. Pie/necklace bag icons
also reuse stock assets. NPC stock clothing does not establish a final uniform.
The old ambiguous work-shirt line is now neutral cloth dialogue; the previous
speaker never identified its owner. No additional bereavement is inferred.

The south road opens after the robbery. Its damaged lower steps mark this small
prototype's endpoint; City2's exact geography is not settled. The local storehouse
connects to future dock buyers. Three small single-Pokemon trainer teams provide
an introductory conflict; rosters/levels remain adjustable. Wilds are visible,
optional encounters, not a new global random-encounter system. The meal does not
heal, and the road fire uses the existing quarter-HP/PP-floor rest rules.

City2's major museum, public sabre display, later Abyss theft and eventual
Suicune/Behemoth Blade resolution are bible-only. City4 is mentioned through the
recipe. No museum/heist/vault room/sabre item/Suicune/ending content is implemented.
The pearls' deeper ecology, the vault's purpose, full city designs, sabre provenance
and the heist's staging remain open. Neither player nor seller knows pearl magic;
Team Abyss does not know the sabre's final purpose at this stage.
