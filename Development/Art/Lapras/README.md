# Tidebound Lapras sprite recipe

Run `python3 Development/Art/Lapras/edit_sprites.py` from the project root.
Inputs: unchanged Graphics/Pokemon/{Front,Back,Icons}/LAPRAS.png.
Outputs: LAPRAS_1.png in Front, Back, Front shiny, Back shiny and Icons.
Battle canvases 160x160; two-frame icon strip 128x64. Logical pixels are 2x2.
Exact palette substitutions preserve original geometry. Eye and forehead marks
are hand-placed pixel clusters; mist is stepped translucent strokes behind the
opaque body. No interpolation, blur or image generation. Shiny palette is
provisional. Original included sprite attribution still applies.
