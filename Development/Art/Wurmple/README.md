# Tidebound Wurmple

The user explicitly authorized direct pixel recolouring on 13 September 2026.
recolour.py replaces the red/coral palette with bright pale blue. It preserves
the original front/back poses, two icon frames, outlines, pixel positions,
shading regions, dimensions and alpha. Cream and yellow details remain.

Sources are the supplied stock Graphics/Pokemon/{Front,Back,Icons}/WURMPLE.png.
Outputs use WURMPLE_1.png. Front/back are 160x160; icon is 128x64. Shiny views
share the pale-blue palette provisionally. No new generated art is used.
Retain the original project Pokemon sprite attribution in CREDITS.md.

Run: python3 Development/Art/Wurmple/recolour.py
