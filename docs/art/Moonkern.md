# Moonkern artwork

A hollow seed with a floating face and leaves.

Edit `assets/Moonkern/pixels.png`; `uv run rebuild --all` exports it through
`art/atlas.py`. The 320×224 atlas contains front/back 160×160 frames across the
top and the 128×64 two-frame icon at bottom left. Normal and shiny share the
approved palette. High-resolution `reference.png` is a design reference; retired
ImageMagick recipes did not reproduce the approved pixels on a current install.

See [the asset guide](../../assets/AGENTS.md) for engine filenames and validation.
