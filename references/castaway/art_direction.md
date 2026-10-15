# Castaway art direction

The island deliberately contrasts the mainland: real warm daylight, cream sand,
turquoise animated water, coconut palms and a cooler, densely wooded interior.
The existing mainland lighting/fog remains unchanged. Working names remain provisional.

The following two assets use the built-in image generation tool. Original source
pixels are retained in their content bundles; the prop renderer supplies display
scale and anchor. The grounded ship reuses the existing approved moored vessel.

## Coconut palm

Approved source: `content/props/island_palm/image.png`.
Native metadata: `content/props/island_palm/prop.json`.

Prompt: Use case: stylized-concept. Asset type: one transparent game prop sprite
for a sunny tropical castaway island in an overhead 2D RPG with classic Pokémon
Gen 3 / RPG Maker XP tile art. A single mature coconut palm tree, leaning gently
to the right, with elegant large drooping green fronds, a few small brown coconuts,
warm ringed tan trunk and small root base. Entire tree isolated, slightly elevated
top-down 3/4 view, trunk base near bottom centre, no cut-off fronds. Clean restrained
professional pixel art, chunky clusters, limited green palette with dark teal
undersides and yellow-green sunlit edges, crisp stepped silhouettes. Suitable at
96 pixels wide and 128 pixels tall relative to a 32px tall player. Transparent
background, no terrain patch, no ground shadow, no text, border or other objects.

## Sailcloth shelter

Approved source: `content/props/castaway_shelter/image.png`.
Native metadata: `content/props/castaway_shelter/prop.json`.

Prompt: Use case: stylized-concept. One isolated transparent prop sprite for an
overhead Pokémon Gen 3 / RPG Maker XP tropical castaway camp. A small improvised
shelter made from a recovered warm cream sailing-ship sail, tied between two
wooden spars, with sturdy visible ropes, two small crates and a rolled sleeping
mat beneath. A broad sloping triangular canvas roof makes real shade, weathered
stitched fabric with a small repaired patch. Compact horizontal 3:2 silhouette,
elevated 3/4 top-down orthographic RPG view, roof above, open front and visible
posts below. Crisp detailed 16-bit pixel art with chunky clusters for final width
112 pixels, limited palette, dark brown outlines and straw-coloured canvas.
Transparent background, no ground, sand patch, trees, people, lettering or frame.

## Native asset integration

Palms have a single solid trunk cell with passable foliage. Dense native tree
groups surround reserved paths. Water uses four native autotile animation frames.
The shelter, filled collecting bowl and raised sail use saved actor availability.
The new Pokémon artwork includes normal/shiny front and back views, party icons
and cries for the selected species and their later evolutions. Data stays native.
