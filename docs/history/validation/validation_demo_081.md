# Tidebound 0.8.1 validation scope

This maintenance release packages the Aipom forest replacement and regional
Normal/Dark Ekans/Arbok already verified on GitHub main. No new story content.

- Forest map 103: Aipom replaces the former Caterpie slot at weight 45, levels
  3–5. Other encounter tables, weights and levels were checked unchanged.
- Native Essentials object tests verify regional snake creation, Poison-free
  level/tutor/inherited egg learnsets, level-22 evolution retaining form 1,
  unchanged ordinary species/stats/abilities, and save-object roundtrips.
- All 264 map events, arrivals and interactions pass the existing map validator;
  editable Ruby sources match the embedded script archive.
- Package version 0.8.1, Mac bundle build 35. Existing mkxp-z runtime,
  fontHeightReporting=1 and save identity Tidebound_Opening_0_2 are retained.
- Release archive integrity and copied payload hashes are checked during
  packaging. GitHub release assets include SHA256SUMS.txt and the source tag.

The agent cannot execute macOS here. Earlier Linux rendered tests belong to
0.8.0; this release uses data/object and package checks, not a new native Mac
or graphical Linux playtest. Test Continue on Monterey, encounter Aipom and a
new regional Ekans, and evolve the latter at level 22. Existing caught ordinary
Ekans/Arbok remain ordinary. New-game Rare Candies remain available.
