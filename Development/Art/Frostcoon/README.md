# Frostcoon art

Run python3 Development/Art/Frostcoon/recolour.py from the game root.
Inputs are unchanged Graphics/Pokemon/{Front,Back,Icons}/SILCOON.png.
Outputs are FROSTCOON.png in those folders and normal-equivalent shiny front/back.
Battle canvases 160x160; two-frame icon strip 128x64. Every source pixel position
and alpha value is retained. Frozen-silk blue, white highlights, golden eye.
No image generation, interpolation, extra anatomy or runtime tint.
The species builder calls this recipe, so rebuilding cannot restore placeholder
white sprites. Original Silcoon sprite and cry attribution remain applicable.
