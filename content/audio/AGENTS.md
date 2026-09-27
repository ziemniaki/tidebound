# Audio

Structure/naming: [architecture](../../docs/architecture.md#authored-content).
Preview syntax: [development](../../docs/development.md#asset-previews).

## Add audio

1. Add an approved Ogg Vorbis (`.ogg`) under
   `content/audio/<music|ambience|cues|effects>/`; it exports byte-for-byte. Put working references
   in `references/`, attribution in `docs/credits.md`. Builds neither synthesize
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
3. Map autoplay belongs to `content/maps/<map>/map.json::music`; battle/victory
   defaults to `content/configure.py`. Both require `uv run rebuild`.
   For Pokémon cries, follow [the Pokémon guide](../pokemon/AGENTS.md) and call
   `GameData::Species.play_cry_from_pokemon(pokemon)`: missing form cries can silently
   fall back to the base. Preview them with `pokemon/ID`.
4. Use `uv run preview "audio/music/<name>"` (substitute the category), then
   listen in-scene with normal/reduced player volume and relevant loop/transitions.
   Stage source/exports and run `uv run check --all`; headers cannot prove sound quality.

`src/tidebound/engine/audio.rb` caps only the two existing Tidebound loops; listen
alongside them when mixing a new track. [Engine contracts](../../docs/essentials-contracts.md).
