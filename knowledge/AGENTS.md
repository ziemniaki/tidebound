# Tidebound knowledge

This directory contains the Git export of one local graph operated by Codex.
Read [README.md](README.md), [KG's guide](../tools/kg/AGENTS.md) and the
[Tidebound integration](../docs/tidebound-kg-integration.md).
For any content work, read and apply [the authoring guide](authoring.md).

- The game bible is creative authority; native source owns implemented behavior.
  Explain proposed material, prototypes, beliefs and intentional mysteries where
  they occur; do not encode them as a lifecycle or mandatory record metadata.
- Read sources and existing graph entities before adding or changing identities.
  Edit through `kg put`, `kg query` or an explicit import, then export here. Do
  not independently edit the live graph and its snapshot as two sources of truth.
- Keep one entity per JSON file under `tidebound/nodes/`, with its outgoing links.
  Source evidence is also in this graph, connected through `sourced_from`. Cite
  imported facts and quotations; do not manufacture citations for new proposals.
  Stable IDs and references survive filenames, code moves and equal display names.
- Write useful dossiers and coherent scenes: concrete habits, relationships,
  creature distinctions, contextual dialogue and drawable visual descriptions.
  Keep new invention explicitly proposed. Do not replace unknowns with generic lore.
- Start with prose. Use structured data for useful details, not a per-kind form.
  Visual descriptions are a single `data.design` string for any subject. Dialogue
  entries have `context` and `text`, with speakers and line breaks in the text;
  cite existing dialogue through `sourced_from` links. Scene beats can include
  options with descriptions of actions and consequences.
  Keep decisions on their subject as `questions`, with optional `options` whose
  entries contain a `description`. These are author decisions; player choices
  belong in scenes. No IDs or status flags for individual questions.
- Develop connected situations: needs, relationships, player actions and visible
  consequences. Link important subjects so an agent can retrieve that context.
  Reuse existing subjects before adding new ones; fold standalone repeated facts
  into their owners. Give relationship qualifiers one `description` string
  directly on the link, including source-section notes. No wrapper object for prose.
  Read descriptions and incoming/outgoing links together: give a relationship
  one account, not paraphrases in both biographies and link descriptions. Leave
  links bare when a scene already explains the interaction; retain any unique
  conditions and proposed/established distinctions on the surviving account.
- Creature work should connect ecology, encounter behavior, raising and evolution.
  Use optional `moves` entries with `name` and `description` for defining techniques;
  check availability against native data. Keep individual starting kits distinct
  from species learnsets, and proposed biology distinct from inherited stock data.
- No scope/development badges, audience lists, save flags, state-machine expressions,
  mirrored test routes, source hashes or filler asset nodes. Describe consequences
  and reveal timing where they matter; native source owns execution and balance.
- All graph queries can contain spoilers. Codex must consider recorded reveal
  conditions when preparing player-facing material or generation prompts.
- Export local changes before a replacement import or branch switch. After
  reconciling Git conflicts, validate the snapshot and explicitly import it.
- `kg validate knowledge/tidebound` checks graph structure. Tests here check
  Tidebound identities and source relationships; they do not execute gameplay.
  Database behavior tests belong in `tools/kg/tests/`; a separate Linux CI job runs both.
- Keep database files in `.build/kg/`, media with their established asset owners,
  and the graph export in Git.
