# KG

One local game knowledge graph, edited and used by Codex. A standalone SurrealDB
process owns the database; the Python CLI and browser UI connect to that same
process. No Docker or cloud database is needed. Codex supplies all reading,
interpretation, authoring and development reasoning; KG supplies storage and queries.

The graph holds entities, relationships, descriptions and structured data for
characters, creatures, locations, items, quests, gameplay rules, dialogue and
assets. It describes gameplay; the actual game engine implements and tests it.

## Install

From the repository root, with uv installed:

```sh
uv tool install --editable ./tools/kg
kg setup
kg serve
```

`setup` downloads the pinned SurrealDB 3.3.0 executable from its official GitHub
release, verifies its SHA-256 checksum, and caches it under `~/.cache/kg/`.
It creates a random local database password in `.build/kg/server/connection.json`
with owner-only permissions. macOS and Linux on ARM64/x64 are supported. The
Python package requires Python 3.12 or 3.13; Windows server setup is not provided.

Leave `kg serve` running in its terminal. Ctrl-C stops it gracefully; restarting
the same command preserves the graph. The server binds only to `127.0.0.1:8000`,
requires authentication and writes its log to `.build/kg/server/server.log`.
The first setup can choose a different port with `kg setup --port 8001`.
Existing setup preserves its credentials and port. Stop the server before editing
the port in `connection.json`.

If `kg` is not on PATH, run `uv tool update-shell` and reopen the shell. After
changing dependencies or moving the checkout, run
`uv tool install --reinstall --editable ./tools/kg`. This package is independent
of Tidebound's build environment. No system-wide database installation is needed.

## Browse locally, without an account

Use the open-source **Surrealist 3.9.12** web app at
[http://127.0.0.1:1420](http://127.0.0.1:1420). It connects to the same local
server as Codex. No remote account, Docker or cloud database is required.
The newer hosted Studio website requires sign-in and is not our default UI.

Keep `kg serve` running. Build the upstream UI once, from the repository root
(Node/npm are needed for the pinned Bun runner; Rust is not):

```sh
mkdir -p .build/kg/ui
curl -fsSL https://github.com/surrealdb/surrealist/archive/refs/tags/surrealist-v3.9.12.tar.gz -o .build/kg/ui/source.tar.gz
printf '%s  %s\n' febd1a4817831394ebd6b9762d073bf52102f007840869e901f9f07c5b6bb9af .build/kg/ui/source.tar.gz | shasum -a 256 -c -
tar -xzf .build/kg/ui/source.tar.gz -C .build/kg/ui
kg_ui=.build/kg/ui/surrealist-surrealist-v3.9.12
cp tools/kg/surrealist.env "$kg_ui/.env.local"
cp tools/kg/surrealist.json "$kg_ui/public/instance.json"
npx --yes bun@1.2.8 install --cwd "$kg_ui" --frozen-lockfile
VITE_SURREALIST_DOCKER=true VITE_SURREALIST_COMPRESS=false npx --yes bun@1.2.8 run --cwd "$kg_ui" build
```

The upstream `VITE_SURREALIST_DOCKER` flag selects its self-hosted build; it does
not run or require Docker. Compression is disabled because the local preview
server serves ordinary assets rather than the precompressed files expected by nginx.
Our configuration disables cloud access, telemetry,
AI integrations, news, support integrations and remote version checks. The UI
source, dependencies and compiled files stay under ignored `.build/kg/ui/`.
We configure the upstream app rather than maintain another frontend.

Start the browser UI in a second terminal, from the repository root:

```sh
npx --yes bun@1.2.8 run --cwd .build/kg/ui/surrealist-surrealist-v3.9.12 preview --host 127.0.0.1 --port 1420 --strictPort
```

Leave it running while browsing; Ctrl-C stops the UI without stopping the database.
On first use, create a local connection named **Tidebound KG** using:

```sh
kg connection
```

Use the endpoint shown there (normally `ws://127.0.0.1:8000`), **Root**
authentication, the generated username/password, and namespace/database `kg`/`kg`.
This is a local database login, not a remote account. The connection command prints
the local password; keep that output private. UI connection preferences belong to
the browser profile. The checked-in UI configuration contains no credentials.

Browse `entity` in the **Explorer** for characters, locations, story facts and
other records; `link` contains relationships with `in`, `out`, `kind` and `data`.
Use **Query** to inspect a neighborhood, then switch its results to graph view:

```sql
SELECT * FROM entity WHERE kind = 'location';
SELECT * FROM link WHERE in = entity:necklace OR out = entity:necklace;
```

Surrealist and Codex see each other's committed changes immediately. Export after
edits from either client. Native edits should preserve KG's stable IDs, required
fields and relationship endpoints. `kg export` validates the graph before writing
a Git snapshot. The earlier inline explorer is only a historical snapshot.

Surrealist is the legacy open-source UI and no longer receives feature updates.
Its pinned version is tested here against SurrealDB 3.3.0; upgrade deliberately.
See its [upstream build instructions](https://github.com/surrealdb/surrealist/blob/surrealist-v3.9.12/CONTRIBUTING.md).

## Use

Run from the repository root:

```sh
kg validate knowledge/tidebound
kg import knowledge/tidebound
kg search necklace
kg show necklace
kg export knowledge/tidebound
```

The default server directory is `.build/kg/server`; its `data/` subdirectory
holds the database. Commands read `connection.json` and connect to the running
server. Use `kg --db /absolute/path/server COMMAND` for another checkout, setting
it up with a distinct port. The database handles concurrent clients and transactions;
the process lock prevents two `serve` commands from owning the same directory.
Keep the directory, credentials and binaries out of Git.

`search` uses native full-text indexes over names, descriptions and nested text
values in structured data. Name and description matches receive more weight
than nested details. Use `--limit 10` to bound results. `show` returns the entity,
its outgoing links and incoming relationships. These are operator views and
include hidden story facts.

Codex can read and write the graph using native SurrealQL:

```sh
kg query .build/kg/question.surql
kg query .build/kg/edit.surql --params .build/kg/parameters.json
```

For example, a query file can contain:

```sql
SELECT name, description FROM entity WHERE kind = 'location';
SELECT ->link[WHERE kind = 'portrays']->entity.* AS subjects
FROM entity:false_koga;
SELECT ->link[WHERE kind = 'sourced_from']->entity.* AS sources
FROM entity:necklace;
```

Query files may contain writes. Use `BEGIN TRANSACTION; ... COMMIT TRANSACTION;`
for related edits that must succeed together. Parameters are JSON values; use
`type::record('entity', $id)` for parameterized record IDs. Return JSON-compatible
values (cast dates or other special database values to strings). Every statement's
errors are reported, including errors after an earlier successful statement.
Structured `put` and `import` preserve arbitrary JSON values, including nulls.
Imports and edits update the native full-text index within their transaction.

For a structured edit, Codex writes one entity to a temporary JSON file and runs:

```sh
kg put .build/kg/necklace.json
kg show necklace
kg export knowledge/tidebound
```

`put` replaces that entity's properties and outgoing relationships in one
transaction. Incoming relationships remain intact. A missing relationship target
rolls back the edit. Read the current entity before editing it so unrelated fields
and links survive. Full-text indexing updates with database writes, including SQL.

## Codex ingestion and development

Ask Codex to read a design passage, conversation or structured content, look up
existing identities, and apply the corresponding graph changes. For structured
JSON exports, use `import`; for a single record use `put`. Codex can also transform
CSV or existing game data into these records. There is no second model behind
an `ingest` or `ask` command.

For example: “Read the lighthouse section of the design spec, update its entities
and relationships, preserve open questions, and export the graph.” Or: “Follow the
necklace's relationships and use that context to implement the next interaction.”

Codex handles meaning, including synonym expansion, relevance, contradictions,
reveal timing and differences between planned and playable scenes. Full-text search and graph
traversal are implemented. Vector indexes are supported by the database, but
embedding generation and vector search commands are not configured: this tool
makes no inference or embedding API calls.

## One graph, small Git files

```text
knowledge/tidebound/
  graph.json
  nodes/
    necklace.json
    mother.json
    source_game_bible.json
```

`graph.json` contains `format: "kg/1"`, `id` and `title`. Each entity file has:

```json
{
  "id": "necklace",
  "kind": "item",
  "name": "Pearl Necklace",
  "description": "The seller’s irreplaceable keepsake of his wife. Remembering its wearer matters more than the pearls’ material value.",
  "links": [{"kind": "belonged_to", "to": "seller_wife"}]
}
```

`data` is optional on entities and relationships. Omit it when there are no
extra properties; writes discard an empty `data: {}`. Nested empty objects and
null values inside meaningful data are preserved. Existing local databases adopt
this field definition when the CLI connects; existing empty objects can be cleared
with `UPDATE entity UNSET data WHERE data = {};` and the same query for `link`.

Kinds and `data` are ordinary content, not a fixed game schema. Start with prose;
use objects and arrays for things such as dialogue, scene order and questions
with options. No scope, status or implementation fields are required. Tidebound’s
[authoring guide](../../knowledge/authoring.md) explains useful dossiers, dialogue,
design prose, branching beats and how to separate established lore from proposals. An outgoing link
is identified by its source, kind and target; it may carry additional structured
data. A plain `data.description` explains a relationship’s condition or meaning;
source links can carry sections. There is no separate schema per relation kind.
In the database, entities are records in `entity`; links are native graph
relations in `link`, with `in` and `out` endpoints. Metadata lives in
`metadata:graph`. Full-text indexes cover `name`, `description` and nested `data`
directly; no `search` property is stored. Object keys are not search prose.

All entity IDs use lowercase `snake_case`: a letter first, then letters/digits
with single underscores between words, at most 180 characters. For example,
`winter_settlement`, `species_arbok_1` and `source_game_bible`. This keeps
record IDs readable as `entity:winter_settlement` without SurrealQL quoting.
Structured writes and the database assertion enforce the same convention,
including browser/SQL edits. IDs are unique; display names need not be and keep
their natural spelling. Filenames are `<id>.json`, but loading uses the IDs
inside files. Nested folders are accepted.
There is no central entity list. Export sorts entities and relationships, preserves
ordered data, removes deleted records and refuses unrelated destination directories.
The snapshot directory contains only its manifest and entity JSON files; keep
README files alongside it. An export validates all relationships before replacing
an existing snapshot.

`import` upserts supplied entities and replaces their outgoing links. It does not
delete entities missing from the snapshot. To restore a complete snapshot after
merging or switching branches:

```sh
kg validate knowledge/tidebound
kg import knowledge/tidebound --replace
```

`--replace` replaces graph contents atomically, including deletions. Export local
changes before doing this. A different graph ID requires a different database
path. Snapshot files are a transport and version-control representation of the
same graph; do not edit files and the live database independently.

## Verification and boundaries

The tests start isolated real SurrealDB servers on temporary loopback ports,
using the same pinned executable and lifecycle as `kg serve`. The first run may
download the executable; no Docker, inference keys or running user database are
needed. They stop their servers and remove only their temporary directories.

```sh
uv run --locked --project tools/kg python -m unittest discover -s tools/kg/tests --buffer
uv run --locked --project tools/kg python -m unittest discover -s knowledge/tests --buffer
```

They cover authentication, concurrent browser/CLI clients, server restarts,
transactions, full-text search, malformed queries and deterministic export/import.
A separate Linux job in `Quick checks` runs both suites. The game’s `check`,
builds and players never start this server; KG has no native platform matrix.

The SDK is pinned in `uv.lock`; the server version and release checksums are pinned
in `server.py`. Upgrade them deliberately with the real-server tests. SurrealDB 3
uses `FULLTEXT ANALYZER`, `type::record`, and `TYPE option<object> FLEXIBLE`.

### Moving from the earlier embedded setup

Export the live graph with the old tool before switching: `kg export .build/kg/embedded-backup`.
Then install the updated tool, run `kg setup` and `kg serve`, and import that backup
in another terminal. Compare a fresh export before retiring the old storage.
Do not point the new server at `.build/kg/world`; it belongs to the older embedded
engine. The default server directory is intentionally separate. Keep the old files
as a recovery backup, not a second graph to edit.

See the official [server documentation](https://surrealdb.com/docs/reference/cli/surrealdb-cli/commands/start)
and [Surrealist source](https://github.com/surrealdb/surrealist/tree/surrealist-v3.9.12).

### Removing the earlier duplicated search field

For a database created before direct field indexing, export a backup, run this
once through `kg query`, then continue normally. Fresh databases need no cleanup.

```sql
BEGIN TRANSACTION;
REMOVE INDEX IF EXISTS entity_search ON entity;
REMOVE FIELD IF EXISTS search ON entity;
UPDATE entity UNSET search RETURN NONE;
COMMIT TRANSACTION;
```

The normal connection creates the three current indexes. This removes only the
old derived text; it does not change authored content.
