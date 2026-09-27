# Artwork sources

Run `uv run rebuild --all` to export registered artwork. `art/compiler.py` is the
export plan; [the asset workflow](../assets/AGENTS.md) covers naming, icon layout,
Essentials fallback and validation. Paths below are relative to the repository.

| Artwork | Editable input | Exporter | Approved details |
| --- | --- | --- | --- |
| Regional Sunkern | `assets/Sunkern/pixels.png` | `art/atlas.py` | Sickly seed, curled leaves, hollow face |
| Moonkern | `assets/Moonkern/pixels.png` | `art/atlas.py` | Hollow seed, floating face and leaves |
| Moonflora | `assets/Moonflora/pixels.png` | `art/atlas.py` | Simple petals, flat muted colours, hollow face |
| Glaciverm | `assets/Glaciverm/pixels.png` | `art/atlas.py` | Pale-blue chitin, cream underside, yellow horn/eyes and rounded omega mouth |
| Regional Wurmple | Stock WURMPLE sprites; palette in exporter | `art/recolors.py` | Pale blue replaces red/coral; cream/yellow details and geometry remain |
| Frostcoon | Stock SILCOON sprites; palette in exporter | `art/recolors.py` | Frozen-silk blue, white highlights, golden eye |
| Regional Ekans/Arbok | Stock EKANS/ARBOK sprites; palettes in exporter | `art/recolors.py` | Gray scales; yellow/orange eyes, belly and hood markings remain |
| Regional Lapras | Stock LAPRAS sprites; pixel recipe | `art/lapras.py` | White/jade palette, green eyes, faded gold scar and sparse translucent mist behind the original silhouette |
| Nivalora | `assets/Nivalora/approved_front.png`, `rear_source.png` | `art/nivalora.py` | Pale butterfly dragon, golden eyes, cream split muzzle, head horn, four wings and curled tail |
| Whyduck | `assets/Whyduck/pieces/` and pixel recipe | `art/whyduck.py` | Pink brain, original Psyduck eye/beak pixels, palms and webbed feet |

Stock sprites are under `game/Graphics/Pokemon/{Front,Back,Icons}/`. Recolouring
preserves every source pixel position and alpha value. Nivalora uses a fixed
16-colour palette and nearest-neighbour sampling. The atlas layout is specified
in the asset guide; high-resolution `reference.png` files and prompts are design
references, not build inputs. Keep them separate from editable pixel atlases.

Current battle canvases are 160×160 and party icons are horizontal 128×64 strips.
Palette edits, atlas species, Lapras and Nivalora use the normal palette for shiny
art provisionally. Whyduck has a separate shiny export. Cry reuse is declared in
`content/verification.py`; copy aliases live in the species catalog.

Species rules belong in [specs/species](../specs/species/), including
[Nivalora](../specs/species/Nivalora.md) and [regional snakes](../specs/species/Snakes.md).
Retain [asset attribution](credits.md) when replacing artwork.
