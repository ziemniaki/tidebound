# Asset exporters and audio

For Pokémon graphics, read [assets/AGENTS.md](../../../assets/AGENTS.md).
The audio workflow below also applies when adding files directly under game/Audio.

## Add music, a sound effect or a cry

Audio files are player assets. Use Ogg Vorbis (`.ogg`) for new music/ambience and
WAV or Ogg for effects; these fit the shipped runtimes. A renamed extension does
not convert the codec. Do not introduce WMA (unsupported by mkxp-z).

| Purpose | Destination | Runtime call (path relative to that category) |
| --- | --- | --- |
| Music | `game/Audio/BGM/<name>.ogg` | `pbBGMPlay("<name>", volume, pitch)` |
| Looping ambience | `game/Audio/BGS/<name>.ogg` | `pbBGSPlay("<name>", volume, pitch)` |
| Short musical cue | `game/Audio/ME/<name>.ogg` | `pbMEPlay("<name>", volume, pitch)` |
| Sound effect | `game/Audio/SE/<name>.wav` | `pbSEPlay("<name>", volume, pitch)` |
| Pokémon cry | `game/Audio/SE/Cries/SPECIES_1.ogg` | `GameData::Species.play_cry_from_pokemon(pokemon)` |

### Workflow

1. Add the playable file with exact case, retaining editable source/recipe under
   `assets/<sound-name>/` if applicable. Record external provenance in
   `docs/credits.md`. Avoid duplicate stems with different extensions: resolution
   chooses an available file, not necessarily the newly added one.
2. Wire playback into the owning scene. Pass `"Door close"`, not
   `"Audio/SE/Door close"`, to `pbSEPlay`. The wrapper adds the category path and
   routes through player volume settings. Calling `Audio.*` directly bypasses
   that integration. Pitch 100 is normal; volume is 0–100. Wrapper fade durations
   are seconds, although lower-level audio calls can use milliseconds.
3. For map autoplay, set `music` on its `MapDefinition` in
   `tools/tidebound_dev/maps/definitions.py`. Battle and
   victory defaults are in `tools/tidebound_dev/content/configure.py`, which writes
   both metadata encodings. Editing the map/PBS output alone is overwritten.
4. Cries use the base ID for form 0 (`SPECIES.ogg`), `_1` for form 1; missing form
   cries fall back to the base. Missing cries may produce silence rather than an
   error. Check `POKEMON` in `art/pokemon.py` before replacing one: full rebuild
   copies those aliases over their destinations.
5. `uv run play` includes a directly added file. If changing generated map/content
   references, run `uv run rebuild --all`, then `uv run check --all`. Listen in the
   actual scene with normal and reduced player volume, including looping and
   battle/map transitions where applicable. Headless checks do not hear audio.

`engine/audio.rb` caps only the two existing Tidebound loops; new tracks do not
inherit that mix automatically. Choose their level by listening alongside them.
The optional ambient generator `tidebound_dev.art.audio` replaces those two loops
and is **not** part of full rebuild. It needs NumPy and ffmpeg; NumPy is not in the
locked project dependencies. Adding a sound does not require running that generator.

Engine methods and runtime support: [Essentials contracts](../../../docs/essentials-contracts.md).
