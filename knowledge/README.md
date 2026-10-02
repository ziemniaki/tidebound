# Tidebound knowledge graph

[tidebound/](tidebound/) is the Git serialization of the game knowledge graph.
Codex reads and edits the live graph through [KG](../tools/kg/README.md), a
local SurrealDB client sharing one server with the browser UI; no Docker or
separate LLM service is needed.

The graph describes the game rather than executing it. The
[game bible](../specs/game-design.md) remains creative authority and native source
owns implemented behavior. The current source review covers game version 0.8.12
at main commit `4135b5c9baa828d2b4246f3b44c4b90b63021433`, inspected on
2 October 2026. The bible retains its 1.31 header with later additions through
section 33. `source_snapshot` records the inspected revision; future main changes
still need source review.

## Use

Follow the one-time [installation](../tools/kg/README.md#install), then run from
the repository root:

```sh
kg validate knowledge/tidebound
kg import knowledge/tidebound
kg search necklace
kg show necklace
kg show source_snapshot
kg export knowledge/tidebound
```

Codex can browse incoming/outgoing relationships, search all descriptive content,
write structured entity JSON with `kg put`, or read/edit with `kg query`. Ask it
to ingest a spec passage or structured source directly; there is no hidden API
model doing extraction. The shared server persists data to
`.build/kg/server/data`. Keep `kg serve` running while using KG or Surrealist;
Ctrl-C stops it. See [browser setup](../tools/kg/README.md#browse-locally-without-an-account).

## Contents and limits

The graph covers authored locations, regional species, household individuals, story
items and NPCs; the opening, oil/necklace progression, Mending, vault, museum,
harbour errands and ring, pond, Hollow Wood and Skull Hollow; and selected wider
canon, decisions and asset descriptions.

Each entity has one file under `tidebound/nodes/` containing its properties and
outgoing links. `graph.json` is a small manifest with no shared entity list.
Entity IDs use lowercase `snake_case`, including source and species IDs; filenames
match the ID. Display names retain their natural spelling.
Source evidence is part of this graph: `sourced_from` links point to source
entities, which point to `source_snapshot`. Source records identify useful reading
and the inspected revision; they carry no
per-file checksum maintenance.

Read [Writing Tidebound’s world](authoring.md) before expanding it. Records contain
readable dossiers, meaningful relationships, species distinctions, creature habits,
contextual dialogue, scene beats and visual direction. The household, regional ecology, necklace sequence and proposed Koga scenes
provide worked examples. Visual
direction uses a single `design` description; scene beats can carry small options
with action-and-consequence descriptions. Meaningful links connect people, objects,
places and outcomes, so retrieval returns the situation around a subject. Proposed
material and real unknowns are marked where they occur.

The earlier audience lists, state declarations, simulation guards/effects and
seven test routes are removed. Native source and tests own execution. Story
conditions, consequences and reveal timing are plain language. Decisions live
inside their subjects as questions with optional descriptions of alternatives;
they need no separate nodes or status fields. Search indexes the real fields directly, including
nested dialogue and visual text. There is no duplicated `search` property.

Try `kg show mother`, `kg show wick`, `kg show species_whyduck`,
`kg show neighbors_pie`, `kg show scene_koga_shared_work`, or
`kg show team_abyss`. A dossier with a concrete
unknown is more useful than invented detail presented as canon. Late chapters
still need authored scenes, decisions and visual references.

Creature records include selected defining moves, evolution relationships and
known acquisition routes. `moves` is a design selection, not a complete learnset.
The household individuals retain their distinct starting kits. The regional
insect and spectral-plant families contain explicitly proposed behavior and care
details, with habitat relationships distinguishing current encounters from proposed
ecological range; native move effects and evolution levels were checked separately against
the pinned engine and authored species data. Stock inheritance is not automatic
approval of regional biology or mythology.

The whole-world review adds connected proposed scenes, material dependencies and
historical evidence: Koga and his communities, the refuge before and after harm,
the oil trade and fencing, shrine visits, and ordinary life beneath the sea.
See [review and remaining decisions](../docs/story-asset-graph.md#whole-world-review).
Tidebound develops continuously; `opening_journey` records the current playable
extent without making the harbour invitation an ending.

The 0.8.12 pass imports the harbour’s named residents, three errands and their
objects, Harker’s ring, the two northern areas and their actual Ghost encounters.
It also checks the repaired pond trail, early pier reveal timing and shared cave
loss recovery. Existing dialogue is quoted from its owner; generated challenger
names do not create fixed NPC identities. The traveller’s broken-bridge line is
recorded as a continuity mismatch with the now-open northern route.

Two people named Toma remain separate identities. Koga and the imitation likewise
remain separate, connected by `portrays`. The necklace stays one unique keepsake.
Psyduck Island and late revelation choices remain unresolved. The old spec's absent
vault, direct-maze opening, road Psyduck and level-33 evolution were superseded by
its later explicit vault visit, false-room sequence, pond and level-16 evolution.

The graph does not transcribe every line of dialogue, stock combat statistic,
audio file or tile. Existing catalogs own those details. Future chapters are
selectively represented, not fully designed or implemented. Native battle outcomes,
capacity limits, timing and save behavior remain the native game's responsibility.

## Editing and merging

Export after live graph changes. Git reviews small entity files; unrelated
additions do not touch a central index. For a merged snapshot, first preserve
local graph work, then validate and restore it explicitly:

```sh
kg validate knowledge/tidebound
kg import knowledge/tidebound --replace
```

Replacement includes deletions. Ordinary import upserts supplied entities and
their outgoing links without deleting absent entities. Both write transactionally.
Do not maintain live graph changes and file changes independently.

A separate Linux CI job runs snapshot and real local-server tests. They establish
graph integrity, source-link targets and browsing behavior, not native gameplay or
creative completeness. Follow the [integration guide](../docs/tidebound-kg-integration.md)
for implementation and asset work.
