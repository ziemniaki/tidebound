# Working on KG

KG is one local SurrealDB knowledge graph, operated by Codex through the `kg`
CLI. Read [README.md](README.md) for installation and commands and the
[design](../../docs/story-asset-graph.md) for scope. Tidebound's export lives in
[knowledge/](../../knowledge/README.md). Python tooling stays here, separately
from `tools/tidebound_dev/`; gameplay stays in its native engine.

- Codex is the only LLM layer. It reads text and structured sources, identifies
  entities, follows relationships, writes updates and uses the graph during
  development. Do not add API clients for inference or embeddings, extraction
  services, Graphiti, agent orchestration, or a second knowledge store.
- Run one standalone server on loopback, shared by the CLI and browser UI. No
  Docker or cloud database is needed. `kg setup` installs the pinned executable
  and local credentials; `kg serve` owns its foreground lifetime. Keep one server
  directory and distinct port per checkout. Never open its files with an embedded
  client. The server handles concurrent connections and transactions.
- Use the pinned upstream Surrealist UI locally, configured by `surrealist.env`
  and `surrealist.json`. No remote account is required. Keep cloud/AI integrations
  disabled; Codex remains the only LLM layer. Do not build a second browser UI.
- Keep the tool small: native graph queries, full-text search, structured writes
  and Git snapshot import/export. Do not recreate a gameplay runtime, formal rule
  language, scenario simulator, approval engine or generation queue.
- The graph describes the entire game design, including behavior and assets.
  Use meaningful entities and relationships, readable dossiers and structured
  `data`. Tidebound content follows [its authoring guide](../../knowledge/authoring.md).
  Add a new kind as data, without changing Python code. Do not add per-kind schemas
  or mandatory scope/status metadata. Omit `data` on entities and relationships
  without extra properties. Put relationship prose directly in the optional
  link `description`; reserve link `data` for structured values. Prose carries
  meaning; small objects and arrays preserve useful structure such as dialogue
  and questions with options.
- Stable IDs identify concepts independently of names, file paths and engine
  symbols. Use lowercase `snake_case` IDs as defined in the README; keep natural
  spelling in display names. Similar names do not imply the same person. Species, individuals and
  their artwork may have different identities. Source evidence is represented
  in this same graph and connected to the concepts it supports.
- Codex edits the live graph. Small JSON files are its Git serialization, not a
  second independently authored design system. Export after edits. Before a
  branch switch or replacement import, preserve local graph changes in an export.
  Reconcile Git conflicts, validate the merged snapshot, then import it.
- Keep writes atomic, reject broken endpoints and duplicate identities, and
  preserve arbitrary JSON data and ordered lists through export/import. The
  native database owns relationships and full-text indexing. Index names,
  descriptions and nested data directly; do not add a duplicated search field.
- Text ingestion is a Codex workflow, not a tool that secretly invokes another
  model. Read existing entities before adding or merging them. Preserve unknowns
  and source evidence. No mandatory operator approval ceremony beyond the user's
  requested scope and creative decisions that actually need an answer.
- All graph access is an author view and may contain spoilers. Codex observes
  recorded disclosure conditions when writing dialogue, briefs or asset prompts;
  the tool does not claim to enforce player visibility or prove gameplay.
- Test against the real local server, including persistence, failed-write
  rollback, search after edits and Git roundtrips. Run `uv run --locked --project
  tools/kg python -m unittest discover -s tools/kg/tests --buffer`. Repository
  CI runs both KG suites in one separate Linux job. Game checks, builds and
  players never open the KG.
