# 0.8.3 squat atmosphere — 25 September 2026

- Regenerated map109, atlas, tile passages and embedded scripts from editable source.
- All sixteen collision masks match the verified 0.8.2 baseline exactly. Map events, maze, guard gates and necklace quest code unchanged.
- validate_maps.py passes every entrance, arrival and interaction across 268 events.
- Only map109 binary changes; other map binaries remain unchanged. New artwork uses cloned atlas entries; shared lighthouse entries retain their pixels .
- Native Linux mkxp-z826929e renders the room under actual map109 tone. Inspected both views in HideoutEvidence_083: cold, legible pathways, no tidy shelving or warm lamps.
- The test-only atmosphere mode is not embedded in release Scripts. Existing full 0.8.2 battle/minigame tests remain the mechanical baseline; no battle logic changed.
- macOS execution is unavailable here; package uses unchanged native runtime, save identity and font fix. User Mac playtest remains necessary.
