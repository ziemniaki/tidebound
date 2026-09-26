# Moonkern sprite source

Built-in image generation and editing, 13 September 2026, with Tidebound
Sunkern as the species/style reference. The first result contained a printed
checkerboard; a second edit replaced it with a magenta chroma key, including
the hollow interior. source.png preserves that corrected atlas. export.sh
removes the key and performs only mechanical crop, palette and size conversion.

Four source cells: front, back, small front and small back. The runtime party
icon uses two positions of the small front to preserve its face while bobbing.
Battle frames are 160x160; icon strip 128x64. Shiny art uses the same palette
pending a separate design. Cry reuses included Sunkern audio provisionally.

Correction prompt: preserve all sprites; remove every checkerboard/background
texture, including inside the hollow seed; use real alpha or uniform #FF00FF
chroma key in all empty regions; retain contour, floating face and leaves.
