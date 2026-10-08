# Tidebound and the knowledge graph

Tidebound uses [KG](../tools/kg/README.md) as a Codex-operated development reference.
One local graph contains game entities, gameplay descriptions, asset needs,
relationships and source evidence. [The design](story-asset-graph.md) defines its
scope; [knowledge/](../knowledge/README.md) contains the Git export.

The game bible remains creative authority, and native source owns actual behavior.
The graph makes those sources easier for Codex to browse together. It does not
compile the game, execute quests, approve new lore or require source filenames
on character and location identities.

## Current contents

The current source review covers game version 0.8.12 at main commit
`4135b5c9baa828d2b4246f3b44c4b90b63021433`. It includes the harbour residents,
errands and ring, repaired pond route, Hollow Wood and Skull Hollow, and the
native pier/recovery changes. The bible retains its 1.31 header with later
additions through section 33. `source_snapshot` records this inspected revision
and its limitations; updating it requires reading changed sources and their meanings.

The household, regional species and opening scenes now carry concrete descriptions,
behavior, contextual dialogue and visual direction. Later canon and unresolved
content remain distinct. Simulation actions and routes have been consolidated
into readable scenes. Decisions sit on their subjects as small questions with
optional alternatives. Prose carries lore and reveal timing; the graph has no
per-kind forms, implementation badges or decision lifecycle. Visual design is
one prose field across subjects. Branching beats reuse small descriptions and
options; links connect the people, objects, locations and conditional outcomes.
Dialogue uses `context` and `text`, with speakers in the text and citations on
source links. Relationship conditions and source notes use a direct `description`.

Sources are concise records linked with `sourced_from`, without mirrored build
manifests or source hashes. Read [the authoring guide](../knowledge/authoring.md)
for dossier contents, grounded creative work, dialogue, asset briefs and disclosure.

## Codex workflow

1. Install KG, start its local server and import the checked-in graph, following its README.
2. Read the authoring guide, relevant game bible passages and owning source guides.
3. Search and traverse the graph to locate existing concepts and dependencies.
4. Deepen a connected situation through `put`, structured import or a native query.
   Reuse its people, objects and places; make needs, actions and consequences
   specific, and connect important subjects with meaningful relationships.
   Ground claims, label proposed invention, preserve mysteries, and keep dialogue
   and visual details consistent with what that scene can reveal.
5. Inspect the changed graph, export it and review the Git diff.
6. When implementing, change the native feature or content owner and run its
   existing build, verification and playtest workflow.

Codex performs text understanding and structured transformation in the current
conversation. There is no direct inference API, embedding service, Graphiti
adapter or second worker orchestrator. KG does not call back into Codex itself.

Ordinary source refactors need no graph change unless game meaning changes.
Code/spec disagreements should be recorded and resolved using the bible's creative
authority and current implementation evidence. Do not promote prototypes or
unresolved names to approved canon merely because they appear in source.

## Native and asset boundaries

Gameplay stays in `src/`; maps, species, items, actors and audio keep their existing
content owners. `tools/tidebound_dev/` remains the only build pipeline. Normal
builds and players do not load the graph or need its database dependency.

Asset descriptions and relationships belong in the graph. Codex uses available
image, audio and coding tools to produce artifacts, then follows the project's
existing approval and integration workflow. The KG tool provides neither media
generation nor another asset pipeline. A concept image does not establish that
a location is implemented.

## Verification

A separate Linux job in `Quick checks` runs the KG and Tidebound graph tests
through KG's own Python environment. These tests start isolated real local
servers without Docker or network inference; game verification does not start
a database. They verify storage, rollback, relationship traversal, search,
source-link targets and portable snapshots. Citations are not mandatory metadata
for every proposed entity. Native gameplay assertions remain in the
existing Ruby and platform harnesses. A graph validation result is not a passing
playthrough or a production readiness certificate.
