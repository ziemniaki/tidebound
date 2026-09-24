# Frostcoon final evolution: sprite milestone, 16 September 2026

Confirmed future Ice/Dragon evolution at level 55. The user approved the front
concept without changes: pale white/blue butterfly dragon, Wurmple golden eyes,
cream split muzzle, head horn, four wings and a curled dragon tail. No name yet.

Included: front.png and back.png (160x160 RGBA battle canvases), icon.png
(128x64, two 64x64 frames, gentle bob), temporary same-palette shiny counterparts.
All game artwork uses binary transparency, at most 16 colours, 72px logical
battle-art bounds doubled with nearest-neighbour scaling. Sources retained:
approved_front.png is the approved original; rear_source.png is the matching
rear-view draft made with the built-in image tool. No front design regeneration.
export.py reproducibly crops transparent fringes, samples and applies a shared
palette that explicitly retains gold eye accents, cream muzzle and blue shading.
Run: python3 Development/Art/FrostcoonEvolution/export.py (requires Pillow).

Installed at Graphics/Pokemon/{Front,Back,Front shiny,Back shiny,Icons}/
FROSTCOON_EVOLUTION.png. This is an ART identifier only, not a registered species.
No arbitrary stats/moves/name are invented. No species or evolution data changes,
no Frostcoon replacement, no save migration. A true rear view is provided, not
a mirrored front. The eventual playable level-55 evolution still needs species
registration, battle data, name, cry and final sprite metrics. Shiny colouring
remains open. Current gameplay is 0.7.11 with this additional art milestone.

Preview.png compares enlarged and game-size assets; icon_preview.gif shows the
two engine icon frames. PNG alpha/dimensions/palette checked and all previews
visually inspected. This is an asset review, not an in-engine battle playtest.

Rear-view revision 2, 16 September 2026: image-right upper wing sweeps outward
and lower. A transparent gap separates its leading edge from the cheek; the
wing root remains below the neck. This corrects the head/wing overlap and adds
a restrained banking pose. Front sprite and party icon remain unchanged.
Original rear source is retained as rear_source_v1.png for revision history.


0.7.12 update: registered as NIVALORA (working display name Nivalora), with
full battle data and level-55 evolution. The art-only status above is historical.
See species_sheet.md. Native metrics: Front 0,4; altitude 8; Back 0,0; shadow 1.
Articuno cry and same-colour shiny remain provisional.
