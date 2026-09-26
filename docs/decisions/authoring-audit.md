# Authoring and integration audit

Audited 2026-09-27 at `b55a75e87f0f23de0e4257556dd7add2378cd365` (0.8.7).
Scope: ownership, coupling, extension points, generation failure behavior and
Essentials contracts for independent feature work. Python migration is out of scope.
This pass adds workflow guidance; the implementation findings below remain open.

The previous refactor removed the implicit execution chains. The remaining work
is at the authoring boundaries: definitions still have secondary owners, generation
can publish incomplete results, and checks do not automatically cover new content.
These are specific extension/verification gaps, not a reason for another framework.

## Findings

### A1 — P2: native species checks can accept missing/wrong artwork

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

**Acceptance:** a new declared species is included without editing a second roster;
removing its required PNG or changing an omitted authored field fails the check.

### A2 — P2: the rebuild plan consumes species before producing them

Evidence: [pipeline.py](../../tools/tidebound_dev/pipeline.py), `rebuild`;
[encounters.py](../../tools/tidebound_dev/content/encounters.py), `build`.
Encounters validates species against the current `species.dat`, but custom species
are compiled afterward. Adding a new species and an encounter in the same change
can fail on a clean base while succeeding if the developer already generated that
species locally. This is an explicit dependency-order defect; existing rosters use
stock species and do not exercise it.

**Change:** put species production before consumers, documenting the few actual
build dependencies in the existing plan. Do not add a task graph framework.

**Acceptance:** one rebuild from a base copy succeeds when a new custom species
and its encounter are introduced together; no preparatory build is required.

### A3 — P2: species generation publishes data before artwork can fail

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

**Acceptance:** a missing source PNG/cry leaves previously playable outputs intact;
the next successful build needs no manual cleanup. One focused failure test suffices.

### A4 — P2: one new map requires edits to several unrelated policy tables

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

**Acceptance:** adding an ordinary indoor map does not require editing separate
native/PBS/tone decisions; it gets validated entries, music and intentional atmosphere.

### A5 — P2: map validation covers only part of the engine's event model

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

**Acceptance:** second-page and out-of-bounds transfer regressions are caught;
computed routes have explicit scenario coverage. Don't build a Ruby parser here.

### A6 — P2: artwork has two different regeneration contracts

Evidence: [species_compiler.py](../../tools/tidebound_dev/content/species_compiler.py),
`export_art`; [Moonkern/export.sh](../../assets/Moonkern/export.sh);
[Lapras/edit_sprites.py](../../assets/Lapras/edit_sprites.py);
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

**Acceptance:** a retained source edit changes the intended outputs in an isolated
rebuild; decoded pixels stay unchanged during recipe migration. Check available
native Windows tools before claiming cross-platform exporter support.

### A7 — P2: actor names encode identity, rendering and collision together

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

**Acceptance:** a duplicate/misplaced actor is rejected during generation and a
label-only rename cannot silently change collision or quest visibility.

## Guidance delivered in this pass

Root AGENTS is a workflow router. Scoped guides cover Ruby features, maps, content,
art, sound, compiled/editor files and tests. They document today's actual owners,
including the limitations above; they do not claim the proposed refactors exist.
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
source and accessible/indexed Essentials documentation. Two disposable probes
confirmed A1's fallback and A3's partial publication. It did not port gameplay,
change assets, or run a new platform build/playthrough. Documentation links and
headless baseline checks are verified for the guidance PR; native behavior claims
remain limited to the inspected contracts and prior release evidence.
