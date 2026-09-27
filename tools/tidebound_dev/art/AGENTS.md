# Asset pipeline and audio

For approved image layouts and prop authoring, use [assets/AGENTS.md](../../../assets/AGENTS.md).

## Pipeline ownership

`pipeline.rebuild` calls `compiler.build` for every play/build/preview/rebuild.
`uv run rebuild --all` also runs map/content compilers. Pipeline entry points:

| Change | Owner in this directory |
| --- | --- |
| File discovery / stock aliases | `files.py::exports` / `ALIASES` |
| Pokémon bundle, shiny or cry reuse | `pokemon.py::POKEMON`; palettes in `recolors.py` |
| File writing / image or audio checks | `export.py::Export.write` |
| Prop metadata validation / Ruby table | `props.py::load` / `write` |
| Native preview selection / rendering | `preview.py` / `preview.rb` |

New files in existing asset categories need no registration; Pokémon need `POKEMON`.
`files.exports` and `pokemon.exports` supply the same records to writing and
`ownership.inventory`; do not add a second source/output list. Destinations are
repository-relative POSIX paths (`game/...`); sources use the supplied root.
Maps register packed textures in `ownership.MAP_OUTPUTS`. `tools/generated/assets.json`
is derived: never hand-edit it or use generated exports as recipe inputs.

Keep retirement **before** writing replacements: case-only renames can otherwise
delete fresh files on macOS/Windows. Fix failed builds and rerun; there is no rollback.
Map references and previews use `props.load`, not separate JSON parsing/validation.
Verify pipeline changes with `uv run check --all` after staging new files: it removes
owned exports in an isolated copy and proves they rebuild from source.

## Add audio

1. Add an approved Ogg Vorbis (`.ogg`) or PCM WAV (`.wav`) under
   `assets/audio/<BGM|BGS|ME|SE>/`; it exports byte-for-byte. Put working references
   in `assets/references/`, attribution in `docs/credits.md`. Builds neither synthesize
   nor re-encode. Renaming an extension does not convert a codec; WMA is unsupported.
   Avoid duplicate stems/extensions: engine resolution can select the wrong file.
2. Call the owning scene's wrapper with a category-relative name:

   | Category | Runtime call |
   | --- | --- |
   | BGM / music | `pbBGMPlay("name", volume, pitch)` |
   | BGS / looping ambience | `pbBGSPlay("name", volume, pitch)` |
   | ME / musical cue | `pbMEPlay("name", volume, pitch)` |
   | SE / effect | `pbSEPlay("name", volume, pitch)` |

   Pass `"Door close"`, not `"Audio/SE/Door close"`. Wrappers apply player volume;
   direct `Audio.*` calls bypass it. Volume is 0–100, normal pitch 100; wrapper fades
   use seconds, while lower-level audio calls can use milliseconds.
3. Map autoplay belongs to `maps/definitions.py::MapDefinition.music`; battle/victory
   defaults to `content/configure.py`. Both require `uv run rebuild --all`.
   For Pokémon cries, follow the bundle declaration in the asset guide and call
   `GameData::Species.play_cry_from_pokemon(pokemon)`: missing form cries can silently
   fall back to the base. Preview them with `pokemon/ID`.
4. Use `uv run preview "audio/BGM/<name>"` (substitute the category), then
   listen in-scene with normal/reduced player volume and relevant loop/transitions.
   Stage source/exports and run `uv run check --all`; headers cannot prove sound quality.

`src/tidebound/engine/audio.rb` caps only the two existing Tidebound loops; listen
alongside them when mixing a new track. [Engine contracts](../../../docs/essentials-contracts.md).
