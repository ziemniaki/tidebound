# Dock ship artwork

Original replacement art for the gloomy night harbour, produced with OpenAI's built-in image generation/editing tool. The moored cargo ship, offshore fishing cutter and small rowboat are authored PNG sources; export preserves their bytes, alpha and geometry. The existing prop metadata sets display scale and event anchors.

## Approved source bundles

- `content/props/moored_ship/image.png` — weathered two-masted cargo vessel, partly furled canvas, raised stern cabin.
- `content/props/offshore_ship/image.png` — lean single-masted fishing cutter with furled sail and nets.
- `content/props/dock_boat/image.png` — open skiff with visible ribs, benches and tucked oars; `dock_boat_left` shares this image with its own anchor.

The existing event IDs, water passage and harbour interactions stay owned by the map and feature. These decorative vessels do not introduce boarding or voyage gameplay.

## Generation prompts

### Cargo ship, initial redraw

Use case: style-transfer
Asset type: transparent pixel-art overworld ship sprite for Tidebound, a gloomy Japanese coastal Pokémon RPG.
Input image 1: the old moored ship sprite to completely redraw. Retain only its broad purpose and orientation (stern on left, pointed bow on right), not its crude silhouette or bland sail shapes.
Primary request: redraw this as a beautifully crafted, believable weather-beaten wooden coastal cargo sailing vessel. A substantial dark hull with layered uneven strakes, tar-dark seams, a narrow gunwale, visible deck planks, a small raised stern cabin, rope coils, modest bundled cargo, two slender masts with believable stays and yards. The sails are worn desaturated grey canvas: mostly furled and one small slack partly lowered sail, not enormous beige rectangles. A tiny dim amber cabin window is the only warm accent. No weapons or people.
Style: authentic restrained 16-bit pixel art, crisp square pixel clusters and stepped edges, as if drawn on a roughly 160 by 128 pixel grid and enlarged with nearest-neighbour. Materials read clearly at a displayed width of 300 pixels. Limited coordinated palette, dark charcoal outlines integrated into shading, no thick cartoon outline. Strong hull volume and clear maritime silhouette; salt wear in controlled pixel clusters. Not an illustration with a pixel filter.
View: slightly elevated three-quarter RPG overworld view, show the top of the deck and near side of hull, left-to-right long axis horizontal, bow points right; no steep diagonal or pure flat profile. Entire ship, mast tips, spars, ropes and keel inside frame with clean transparent margins. Single ship, wide composition. Tiny sparse slate waterline pixels immediately beneath hull, no sea rectangle or scene.
Palette and mood: night harbour, cool weathered grey-brown timber, charcoal and muted blue-grey shadows, dull ash-grey sailcloth, sparse subdued cold highlights. Moody and grounded, poor working harbour, sombre and beautiful. Avoid saturated red, bright tan/gold, white sails, cute toy proportions, clip-art, smooth gradients, painting, blur, glossy lighting, skull flags, text, checkerboard painted into image, background landscape.
Deliver an actual transparent PNG sprite with crisp alpha silhouette and transparent spaces inside the rigging. Output artwork only.

### Cargo ship, transparency cleanup

Use case: background-extraction.
Edit target: this generated pixel-art cargo ship. This is a production sprite for a 2D game.
Change ONLY the transparency and the pixels outside the actual vessel: remove EVERY diffuse brown/grey halo, glow, dark vignette, haze, blur, ambient light cloud, soft shadow and painted background around the ship. Remove the broad reflected-water patch beneath it. Retain at most a few crisp broken 1-pixel blue-grey waterline marks directly touching the hull. All negative space, including between ropes and masts, MUST be fully transparent alpha=0. Solid ship pixels should be opaque; do not fade the ship. Use hard clean stepped pixel alpha edges.
Keep the exact existing ship design, colours, pixel texture, rigging, cabin, sails, horizontal right-facing orientation and framing. No redesign, no scenery, no additional objects. Do not draw a checkerboard. Deliver a tightly clean transparent PNG sprite, with the entire vessel inside the canvas.

### Offshore fishing cutter

Use case: style-transfer.
Asset type: single transparent pixel-art overworld offshore fishing ship sprite for the gloomy coastal RPG Tidebound.
Input 1 is the old crude ship to replace entirely. Input 2 is the new cargo ship's art style reference, not the desired ship design. Input 3 is the actual game scene for pixel scale and palette reference; do NOT draw that scene.
Redraw the offshore vessel as a distinct lean weathered fishing cutter, one tall mast, sloping boom with a completely furled narrow dark grey sail, a low roofed cabin aft on the LEFT, a long pointed curved bow on the RIGHT. Give it a believable exposed deck, ribbed net bundles, working ropes, fenders, a little anchor, tarred hull planks, a battered gunwale, and a small dim amber stern window. It should feel like a quiet, exhausted working ship tied offshore at night. Not a two-masted copy of the cargo ship.
Style: authentic crisp 16-bit RPG pixel art, deliberately large coherent stepped square pixel clusters as if painted on a 160 by 128 grid and enlarged nearest-neighbour; detailed but very readable when displayed about 280 pixels wide. Elevated three-quarter overworld view with visible deck and front hull face; long horizontal axis, bow faces right. Match the muted charcoal, weathered grey-brown wood and sparse cold ash highlights of reference 2. No saturated colours or bright beige canvas. No people, weapons, text, symbols, skull flags or ornate galleon decoration.
Production transparency is critical: fully transparent background and fully transparent holes between all rigging, crisp solid alpha edges, no diffuse halo, no glow, no haze, no shadow cloud, no vignette, no sea plane, no reflection. Only a handful of crisp broken slate-blue waterline pixels directly touching the hull. Entire boat, mast tips and rigging inside the canvas with transparent margins. Artwork only; actual transparent PNG.

### Rowboat

Use case: style-transfer.
Asset type: one transparent small rowboat/skiff sprite for Tidebound, a gloomy night-time pixel-art coastal RPG.
Input 1 is the old crude little rowboat to completely redraw. Input 2 is the new large ship's restrained timber pixel-art style reference. Input 3 shows the actual game dock, palette and intended rowboat scale; do NOT render the scene.
Create one simple believable empty weather-worn wooden harbour rowboat. Long horizontal hull, rounded flat stern LEFT and pointed bow RIGHT, elevated three-quarter overhead RPG view: see clearly into the boat, open dark interior, three thin cross benches, curved ribbing and tarred plank seams, one pair of slender oars resting tucked inside along the gunwales, a tiny rope coil in the bow. Good hull volume, not a flat rectangle. No cabin, roof, mast or sail.
Authentic sharply clustered 16-bit pixel art. Designed to read at only 90 by 40 game pixels: strong small silhouette and sparse legible detail, about 48 by 24 deliberate pixel cells enlarged nearest-neighbour, not high-definition texture. Muted grey-brown timber, charcoal shadow interior, desaturated slate highlights. Sombre and worn, no toy/cartoon look, no thick uniform black outline, no saturated orange or white.
Single wide boat centred with modest transparent margins, entire bow and stern inside frame. Production transparency: solid crisp stepped edges; background and all empty space outside the silhouette alpha=0. NO diffuse glow, halo, water reflection, soft shadow, haze, vignette, scene, text, characters or checkerboard. Can have two short crisp blue-grey waterline marks immediately touching the hull. Output actual transparent PNG artwork only.


### Native night palette correction (all three vessels)

The shared correction below was applied to each vessel with its own native dock screenshot as the diagnostic reference. Tidebound's existing night tone stays unchanged; the approved sprite midtones account for that renderer.

Use case: lighting-weather.
Asset type: production transparent pixel-art RPG vessel sprite, colour correction for native night lighting.
Input 1 is the EXACT sprite to edit. Input 2 is a DIAGNOSTIC screenshot showing the same sprite in-game; it is not the output scene. The engine applies a strong night tone (-80 red, -74 green, -48 blue, substantial desaturation), causing the ship's deck and timber to turn almost pure black. We need a brighter SOURCE sprite; the engine will make it gloomy again.
Edit ONLY the colour values within the vessel in input 1. Preserve its exact design, silhouette, orientation, proportions, rigging, pixel clusters, transparent margins and composition. Do not add a background or modify the game screenshot.
Lift the timber, deck, cabin, ropes, gunwales and bench midtones MUCH MORE than a subtle correction: use weathered silver-grey driftwood and ash-brown, with the majority of wooden midtones at RGB approximately (145,140,130), shadow planes around (110,112,117), worn highlights (180,177,167). Dark recessed seams and outlines may remain around (65,68,76). The vessel body must be clearly visible against a dark surface. Bring ropes and deck fittings up to similar readable midtones. Keep sails a restrained pale grey (around 180–205) and keep the existing tiny amber window, if present. No saturated gold, orange or bright tan; no white glare. This is daylight-value source art for a darkened GAME renderer, not already darkened night artwork. Both hull sides and upper deck need readable tonal structure after subtracting about 75 brightness levels.
Keep hard, crisp, stepped pixel-art marks; no painting, blur or smooth gradient. Preserve actual transparency and alpha silhouette. All spaces outside the boat, including inside rigging, remain fully transparent; no diffuse halo, painted glow, shadow cloud, vignette or water reflection. Only retain existing short hard pixel waterline marks. Deliver just the brighter transparent source sprite, full vessel in frame, same framing and aspect ratio as input 1.
