# Artwork

Approved pixels are build inputs. Export preserves geometry, alpha and pixel
colours; it does not resize, quantize or reinterpret art. Concepts and working
material live in root `references/`. Species design lives in
[specs/species](../specs/species/); retain [attribution](credits.md) when replacing art.

The [content guide](../content/AGENTS.md) covers authoring and engine contracts.
[Architecture](architecture.md#authored-content) defines the single directory and
naming convention; [development](development.md#asset-previews) documents previewing.

Stock fonts, battlebacks, animations and interface resources remain engine inputs.
Essentials resolves some filenames dynamically; text search alone cannot prove
an asset unused. Battleback metadata names a set (`_bg`, `_base0`, `_base1`,
`_message`), and animation databases reference graphics independently of source
code. Preserve those contracts when replacing stock assets. Keep
`fontHeightReporting: 1`; fonts and native layout need visual inspection.
