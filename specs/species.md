# Species design notes

The [game bible](game-design.md#7-pokémon-and-the-regional-pokédex) owns narrative
canon. Exact stats, evolution thresholds, learnsets, Pokédex text and sprite
metrics live in the linked `species.json` bundles. These notes retain the design
intent and constraints behind those values; encounters belong to the maps.

## Frostcoon and Nivalora

Data: [regional Wurmple](../content/pokemon/WURMPLE_1/species.json),
[Glaciverm](../content/pokemon/GLACIVERM/species.json),
[Frostcoon](../content/pokemon/FROSTCOON/species.json),
[Nivalora](../content/pokemon/NIVALORA/species.json).

Regional Wurmple's native personality split gives roughly equal chances of
Glaciverm or Frostcoon. The branch is fixed per individual and cannot be rerolled
by cancelling evolution or saving. Glaciverm is the finished early branch;
Frostcoon requires a much longer investment before becoming Nivalora. Narrative
rarity does not change that split. The line retains Medium growth; Nivalora's
pseudo-legendary stat total does not justify changing existing experience curves.

Frostcoon is a slow, defensive Bug/Ice support cocoon. Its moves provide hazards,
healing, weather and disruption; it has no direct damaging attacks or field
healing. Hazards and Hail can still cause indirect damage. Its severe Fire/Rock
weaknesses constrain its bulk. Shell Armor protects against critical hits.
Four move slots require choosing between these roles.

Nivalora is a rare, beautiful, benevolent Ice/Dragon butterfly: a very fast special
attacker with strong special bulk and weaker physical defence. Its airborne art
does not grant Flying typing or Levitate. Shield Dust blocks damaging moves'
additional effects, not direct status moves. Poison-inflicting moves are excluded;
normal paralysis/freezing effects and Sleep Powder accuracy remain. Dragon Dance
raises Attack/Speed; later Quiver Dance supplies special setup.

Both retain the ordinary limits of their support moves. Wish heals the occupant
of its position on the following turn; Life Dew heals active allies, not the
bench. Hail enables Aurora Veil, and Rain Dance reduces incoming Fire damage.
Sleep and paralysis are alternatives, not simultaneous effects. Nivalora's Roost
leaves its typing unchanged. These moves do not cure poison, revive fallen
Pokémon or grant field healing. Rest, Heal Bell, Aromatherapy and Healing Wish
are not granted to Nivalora.

Frostcoon keeps Silcoon's native pixel geometry with pale-blue frozen silk, white
highlights and golden eyes. Nivalora has white/pale-blue wings, Wurmple's golden
eyes, a cream split muzzle, head horn and curled tail; retain the corrected rear
wing pose. Both currently share their normal palette with shiny individuals.
Silcoon and Articuno cries are provisional reuse, respectively.

Evolution retains identity, items, history and existing moves. Nivalora offers
Dragon Breath on evolution and Ice Beam at the threshold; ordinary move-reminder
rules cover missed moves. Cancelling or using Everstone works normally; existing
high-level Frostcoon qualify at their next level-up. No wild Nivalora encounter
or new TM/tutor location is implied by its move compatibility.

## Whyduck

Data: [regional Psyduck](../content/pokemon/PSYDUCK_1/species.json),
[Whyduck](../content/pokemon/WHYDUCK/species.json).

The Water/Psychic regional Psyduck retains familiar Psyduck art and base stats.
Ordinary Psyduck and Golduck remain distinct and existing owned individuals keep
their forms. Whyduck is a strong special attacker with substantial special
resilience and a comparatively frail physical side. Psychic techniques, aquatic
moves, Calm Mind and recovery supply its battle identity.

Inspired by the supplied penguin pose, Whyduck retains a rounded Psyduck-yellow
body, orange flank/golden belly, duck bill, small feet and short tail. Its arms
make an asymmetric incantation pose away from its head. The opened skull has a
jagged bone rim, inner shadow and broad pink brain with uneven hemispheres and
winding folds. It must read as exposed brain tissue, never a flower or hat. Its
relationship to other magic remains unknown.

Approved Gen 3 sprites retain original bill, eye and hand pixels, with pupils
looking down-left and the casting pose mirrored in back view. The shiny has a
blue body and green brain. Front/back views and two icon frames use the native
2x pixel grid. Psyduck's cry remains a placeholder.

## Regional Ekans and Arbok

Data: [Ekans](../content/pokemon/EKANS_1/species.json),
[Arbok](../content/pokemon/ARBOK_1/species.json).

Gray scales preserve the native pixel shapes, eyes, belly bands and hood markings.
Both forms are Normal/Dark; stats and abilities stay unchanged. Every Poison-type
move is replaced, including status moves. The design mapping is:

| Poison move | Dark replacement |
| --- | --- |
| Poison Sting | Pursuit |
| Acid | Snarl |
| Acid Spray | Assurance |
| Sludge Bomb / Sludge Wave | Dark Pulse |
| Gastro Acid | Taunt |
| Belch | Foul Play |
| Coil | Hone Claws |
| Gunk Shot | Throat Chop |
| Poison Jab | Crunch |
| Venoshock | Payback |
| Poison Fang | Jaw Lock |
| Poison Tail | Night Slash |

Pursuit supplies an early weak attack; Snarl retains special damage with a
stat-lowering effect. Later physical moves suit the original Attack stats.
Hone Claws retains Coil's Attack/accuracy setup without raising Defense. Taunt
provides disruption instead of ability suppression. These are role substitutions,
not promises of equal power or effects. Level-up move levels stay unchanged;
remove tutor duplicates while preserving other moves and ordinary forms.
