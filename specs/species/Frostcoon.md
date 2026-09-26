# Frostcoon — Tidebound 0.7.12

Bug/Ice · Frozen Silk Pokemon · Shell Armor (prevents critical hits)

| Stat | Base value |
|---|---:|
| HP | 65 |
| Attack | 35 |
| Defence | 95 |
| Special Attack | 55 |
| Special Defence | 85 |
| Speed | 15 |
| Total | 350 |

A slow defensive support cocoon. It sets hazards, restores HP, changes weather
and disables opponents. Shell Armor prevents critical hits. Fire and Rock remain
4x weaknesses; Flying and Steel are 2x. It resists Grass, Ground and Ice.
All granted moves are status category; hazards and Hail retain indirect damage.

Wish heals the occupant of its position at the end of the next turn, allowing a
teammate to switch in. Life Dew restores one quarter HP to the user and active
allies, not benched Pokemon. Neither move cures poison. Hail enables Aurora Veil;
Rain Dance also reduces incoming Fire damage. Sleep Powder and Stun Spore use
native accuracy and immunities; sleep/paralysis are alternatives, not simultaneous.
Four move slots require choosing between these roles. No new field healing.

## Evolution

Regional Wurmple -> level 10, fixed native Cascoon personality branch -> Frostcoon.
The other branch yields Glaciverm. The split is approximately 50:50 and cannot
be rerolled by cancelling evolution or saving. At level 55 Frostcoon now evolves into Nivalora, the Ice/Dragon final stage.
Its supporting identity and existing moves carry through normal evolution.

## Level-up moves

| Level | Move |
|---|---|
| Evolution | Spikes |
| 1 | Harden |
| 1 | String Shot |
| 10 | Wish |
| 13 | Stun Spore |
| 16 | Rain Dance |
| 19 | Protect |
| 22 | Life Dew |
| 25 | Sticky Web |
| 28 | Sleep Powder |
| 31 | Hail |
| 34 | Aurora Veil |
| 38 | Reflect |
| 42 | Light Screen |
| 46 | Safeguard |
| 50 | Baton Pass |
| 54 | Wide Guard |

## Machine/tutor compatibility

Protect, Endure, Substitute, Safeguard, Light Screen, Reflect, Hail, Rain Dance,
Iron Defense and Helping Hand. No egg moves or hidden ability. Compatibility
does not add tutors or item locations. No damaging moves or status-curing moves.

## Pokedex entry

It seals itself in silk glazed with frost. Even when its shell lies perfectly
still, a faint scratching can be heard from within.

## Supporting data

Height 0.7 m; weight 12.0 kg; catch rate 120 (an engine parameter, not a percentage);
base experience 95; yields 2 Defence EVs; Medium growth; starting happiness 50;
50:50 gender ratio; Bug egg group; 3,840 hatch steps; no held-item drops.

## Art and compatibility

Manually recoloured Silcoon front/back sprites and two-frame icon: pale-blue
frozen silk, white highlights, golden eye. Original geometry and transparency
preserved. Shiny currently shares normal art; cry reuses Silcoon.
Existing saved Frostcoon retain identity, level, IVs/EVs, item, status and actual
current HP. Selected status moves keep their PP. Old damaging moves are replaced
with available support moves; their PP is capped to the old slot's remaining PP.
The same normalization removes inherited attacks when Wurmple evolves.
Older provisional stats and obsolete Shed Skin still refresh once on load.
Fainted or fallen Pokemon are not revived. Art and base stats are unchanged.
