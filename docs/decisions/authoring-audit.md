# Authoring and integration audit

Audited 2026-09-27 at `b55a75e87f0f23de0e4257556dd7add2378cd365` (0.8.7).
Scope: ownership, coupling, extension points, generation failure behavior and
Essentials contracts for independent feature work. Python migration is out of scope.
All seven findings below are implemented in focused commits on PR #16.

The previous refactor removed the implicit execution chains. The remaining work
is at the authoring boundaries: definitions still have secondary owners, generation
can publish incomplete results, and checks do not automatically cover new content.
These are specific extension/verification gaps, not a reason for another framework.

## Findings

### A1 — Implemented: derive native coverage from the content catalog

Evidence: [native_scenarios.rb](../../tests/native_scenarios.rb),
`species_snapshot` and `species`; Essentials `Species_files#check_graphic_file`.
The snapshot and art rosters are hardcoded. Snapshot comparison omits metrics,
cries, egg/tutor moves and other attributes. Art verification only asks whether
loading returns a nonempty bitmap; the resolver can return base-form, normal or
`000` placeholder art instead of the requested asset. New species can be absent
from both lists and receive no check.

**Reproduced:** loaded the shipped Species_files section in the Ruby WASM runtime
with a resolver exposing only `Graphics/Pokemon/Front/000.png`. Requesting a missing
species, form 1 and shiny succeeded with that placeholder. This demonstrates the
fallback contract, not a missing asset in the current release.

**Change:** pass the custom content inventory into the existing native fixture.
Compare the supported authored fields and metrics, and assert exact resolved paths
for required assets, allowing explicitly declared reuse. Keep one species scenario
inside existing native runs; no additional platform/path jobs.

**Verified:** inventory tests include a new declared species without a second roster.
The native ARM scenario compares every custom species/metric attribute except PBS
bookkeeping and non-evolving backlinks, and checks exact sprite/icon/cry paths.
Disposable native fault probes reject a removed shiny sprite despite normal-art
fallback, and reject altered front-sprite metrics. Catalog merges also reject
duplicate IDs instead of silently replacing a definition.

### A2 — Implemented: produce species before their encounter consumers

Evidence: [pipeline.py](../../tools/tidebound_dev/pipeline.py), `rebuild`;
[encounters.py](../../tools/tidebound_dev/content/encounters.py), `build`.
Encounters validates species against the current `species.dat`, but custom species
are compiled afterward. Adding a new species and an encounter in the same change
can fail on a clean base while succeeding if the developer already generated that
species locally. This is an explicit dependency-order defect; existing rosters use
stock species and do not exercise it.

**Change:** put species production before consumers, documenting the few actual
build dependencies in the existing plan. Do not add a task graph framework.

**Verified:** a focused test adds a previously absent species and a roster using
it, then runs the plan against copied native databases. The first build succeeds
and the resulting encounter refers to the new species.

### A3 — Implemented: stage the full rebuild before publishing

Evidence: [species_compiler.py](../../tools/tidebound_dev/content/species_compiler.py),
`build` writes both databases and PBS, then calls `export_art`. Full rebuild also
publishes each operation separately. Maps validate in a temporary workspace, but
their final per-file copy is not a whole-tree transaction either.

**Reproduced:** in a disposable copy, changed Whyduck's name and injected a missing
artwork failure in `export_art`. The build raised while changed `species.dat` and
`pokemon_whyduck.txt` were already present. No live files were modified by the probe.

**Change:** generate and validate a complete content result in a temporary root
before publishing its declared output set. Separate data compilation from art
export so failure ownership is visible. Define what happens if publication itself
fails rather than promising an atomic multi-file operation without implementing it.

**Verified:** failure tests cover a late artwork error, rollback after a mid-publish
I/O error, removal of newly published files and successful retry without cleanup.
Data compilation and art export are separate operations. Full rebuild validates a
disposable result before publishing; rollback failure retains the recovery path.
Process termination is explicitly not claimed to be crash-atomic.

### A4 — Implemented: consolidate authored map settings

Evidence: [compiler.py](../../tools/tidebound_dev/maps/compiler.py), `construct`;
[registry.py](../../tools/tidebound_dev/maps/registry.py), `MAPS`;
[validate.py](../../tools/tidebound_dev/maps/validate.py), `spawns`;
[model.py](../../tools/tidebound_dev/maps/model.py), `Map.serialize`;
[serialization.py](../../tools/tidebound_dev/maps/serialization.py), `serialize`;
[configure.py](../../tools/tidebound_dev/content/configure.py), `build`;
[atmosphere.rb](../../src/tidebound/world/atmosphere.rb), `atmosphere`.
Music, arrivals, native/PBS metadata and indoor tone classification are separate.
The same battle environment/background decisions occur in two encodings. A new
registered map without an entry in `spawns` fails with a KeyError; a new indoor map
can silently receive outdoor fog/tone. Shared tables also create avoidable conflicts
between agents adding different areas.

**Change:** give each authored map a small explicit definition containing its ID,
arrivals, audio and metadata; use it for both encodings and generated Ruby policy.
Keep the explicit builder composition and named painters. No new map DSL.

**Verified:** a new-map fixture supplies one definition and receives consistent
native/PBS metadata, music and generated indoor atmosphere. Arrivals come from
that same definition. Regenerating the current maps preserves their binaries,
metadata and preview pixels; only the generated runtime settings and their Ruby
consumer change.

### A5 — Implemented: validate all event pages and declare ordinary transfers

Evidence: [validate.py](../../tools/tidebound_dev/maps/validate.py), `validate` uses
`@pages[0]` and regexes matching positive literal coordinates with specific spacing.
Essentials selects the last matching event page and executes arbitrary Ruby.
A later page, negative coordinate, computed destination or differently formatted
transfer can escape those scans. The success text currently says every arrival,
door and interaction is reachable, which exceeds this evidence.

**Change:** validate every authored page and represent ordinary transfers as
structured builder data before generating Ruby. Bounds-check before indexing masks.
For conditional/scripted movement, require a targeted scenario and state the static
check's limits. Retain small public Ruby event calls for story logic.

**Verified:** regressions reject missing artwork and direct/computed travel on a
second page, native Transfer Player commands, negative/oversized coordinates and
blocked destinations. Coast source offsets are applied once; destinations are
absolute. Checkpoint returns remain covered by the opening/neighbor/hideout flows.
Dream/folded-room arrival, retry and both conditional return routes are covered
in `world_boundaries.rb`. Static validation explicitly excludes arbitrary Ruby
routing; feature changes need their own route scenarios.

### A6 — Implemented: one portable pixel export plan

Evidence: [species_compiler.py](../../tools/tidebound_dev/content/species_compiler.py),
`export_art`; `assets/Moonkern/export.sh` (retired);
`assets/Lapras/edit_sprites.py` (moved to `art/lapras.py`);
[pipeline.py](../../tools/tidebound_dev/pipeline.py).
Full rebuild regenerates some artwork but copies/retains other exported PNGs.
Changing a retained source atlas can pass `check --all` because that recipe never
runs. Species compilation also owns artwork export and overwrites selected files.
Some per-species recipes need shell/ImageMagick/fonts outside the locked Python
environment. Ambient audio likewise needs unpinned NumPy and external ffmpeg.

**Change:** move repeatable pixel-export code into callable art modules with explicit
inputs/outputs, invoked from one export plan. Keep external sound production optional;
declare its reproducible environment only if maintaining generated audio is desired.
Do not rerun image generation or redesign approved art as part of this cleanup.

**Verified:** a full export compares every Pokémon PNG against approved decoded
pixels and a source-atlas edit reaches normal and shiny output. Imports perform
no file I/O. Wurmple/Lapras/Nivalora recipes now run through callable Pillow modules.
All four legacy ImageMagick recipes reproduced different pixels with the available
Mac installation. Instead of carrying that hidden dependency forward, approved
pixel atlases are now authoritative, with original high-resolution art retained as
reference. Obsolete shell recipes/intermediates were removed. Pixel output remains
unchanged. Native Windows evidence belongs to the final platform verification;
optional audio production remains outside the rebuild contract.

### A7 — Implemented: map-qualified identities and explicit actor roles

Evidence: [registry.py](../../tools/tidebound_dev/maps/registry.py), `ACTORS` and
`write_registry`; [navigation.rb](../../src/tidebound/world/navigation.rb), `actor`;
[actors.rb](../../src/tidebound/features/actors.rb), `visible?` and `sync`.
The registry checks that a name exists somewhere. Lookup searches only the current
map and returns its first match. Separate prefix/string checks select companion,
quest visibility and collision behavior. Copying a `Wild:` name can opt a new actor
into another quest's policy; renaming a readable label can disconnect a scene.

**Change:** first validate registered actors against their owning map and reject
ambiguous matches. Then give special actors explicit role/state ownership in the
existing registry, migrating consumers together. Keep this as data and small
functions; no entity-component system or plugin registry is needed.

**Verified:** generation rejects duplicate/misplaced identities, unknown roles
and missing role fields. A label-renaming fixture preserves identity, placement
and collision data; Ruby quest scenarios use deliberately renamed actor labels.
Headless collision tests retain key/bird visibility and ignore a misleading
`Wild:` label on an unregistered event. All presentation selectors now read roles,
assets and threshold directions rather than event display names. Existing event
order and map binaries are unchanged.

## Guidance delivered in this pass

Root AGENTS is a workflow router. Scoped guides cover Ruby features, maps, content,
art, sound, compiled/editor files and tests. They document today's actual owners,
including static/native verification limits and the implemented ownership contracts.
[Essentials contracts](../essentials-contracts.md) records the versioned sources and
inspection method. The repository workflow defines integration of shared generated
binaries from independent checkouts. Stale migration/PR-in-progress instructions
are corrected in place.

## Order and verification

Fix A2/A3 first: build order and failure publication affect reliable authoring.
Then A1, extending the existing check without buying more CI minutes. A4/A5 belong
together when extending map authoring; A6 and A7 can be separate changes with clear
output/identity ownership. Each should have a focused commit and evidence.

This audit used call-site tracing, the current embedded engine, upstream v21.1
source and accessible/indexed Essentials documentation. Disposable probes confirmed
fallback and partial-publication defects. Implementation verification covers
headless flows, isolated regeneration, exact artwork/metrics and native scenarios;
platform verification is recorded in the PR. This is maintenance, without a
Python gameplay port, save migration framework or expanded CI path matrix.
