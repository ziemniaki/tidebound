# Glaciverm artwork

source.png is the retained built-in image-generation atlas, made for this
project. export.sh mechanically crops its front/back views, reduces the palette
to 12 colours, scales with nearest-neighbour sampling and creates a two-frame
party icon. No runtime generation or filtering is needed.

Brief: original frost-caterpillar evolution, elongated armoured worm/snake,
simple chunky handheld-RPG pixel shapes, stern readable eyes, pale-blue chitin,
cream underside, short pale-yellow forehead horn linking it to Wurmple. No
wings, dragon anatomy, aura, particles or elaborate texture. Two matching
front/rear three-quarter views on a transparent background.

Battle frames: 160x160. Icon: 128x64. Shiny artwork currently shares the normal
palette. A separate shiny colour design remains open. The cry provisionally
reuses the included Wurmple cry; original asset credits remain applicable.


0.7.7: the user requested Wurmple's rounded mouth as a family connection.
mouth_detail.py applies the direct pixel refinement to the exported front
view before enlargement and icon generation. It replaces the grin with a
cream protruding snout and lip crease using existing palette colours. The
original atlas remains unchanged so the complete edit can be reproduced.


0.7.9: mouth_detail.py adds yellow Wurmple-like eyes and a deeper omega-shaped
snout notch. icon_detail.py restores the yellow eye rim after icon reduction.
Run Art/Glaciverm/export.sh (from Development) to reproduce the complete edit.
Rear sprite, body and gameplay data remain unchanged.
