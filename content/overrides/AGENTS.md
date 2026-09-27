# Native stock overrides

Files here replace the same relative path in the Essentials baseline before
compilation. Keep exact engine filenames/case. Normal custom content belongs in
its dedicated bundle, not here. The shared [editor workflow](../../docs/development.md#rpg-maker)
covers importing saved native edits and resolving conflicts.

- `Game.ini`, `mkxp.json`, `Data/System.rxdata`, `Data/metadata.dat` and
  `PBS/metadata.txt` own project defaults. Keep metadata PBS/native values aligned;
  Essentials can recompile PBS in debug mode. System start location is authored;
  only its map-cache revision is generated.
- Stock maps/assets and native editor databases can be overridden. Imported
  `MapInfos.rxdata` and `Tilesets.rxdata` omit authored map/tileset records; never
  copy their complete generated databases here. Prefer a map/tileset bundle when
  adopting stock content into ongoing Tidebound development.
- Generated scripts, custom species/PBS and bundle assets have source owners.
  The build rejects overriding those files. Engine Ruby changes belong in
  `tools/tidebound_dev/scripts/patches.py`; custom gameplay belongs in `src/`.
- Do not edit `runtime/essentials/base.zip` for game changes. Deleting an override
  restores the baseline on the next build. Never force-add `game/` outputs.
