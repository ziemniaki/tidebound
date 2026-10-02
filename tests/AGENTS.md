# Testing and verification

Run commands from the repository root. `uv run check` prepares locked Node
packages, assembles the native project, extracts its archive and supplies fresh map-event scripts to the harness.
No committed game outputs are needed. Stage new sources before `check --all`:
its isolated build copies only Git-tracked paths.

## Commands and suite boundaries

| Location | What it protects |
| --- | --- |
| `tooling/` | Compiler dependencies, map editing/reachability, archives, releases and save isolation |
| `gameplay/` | Companion identity, battle rollback, quest retries, saves and sprite resources |
| `native/` | Packaged runtime startup, rendering, real engine saves and platform path handling |
| `support/` | Explicit engine doubles and shared headless setup |
| `../knowledge/tests/` | Tidebound graph identities, source relationships and real graph browsing |
| `../tools/kg/tests/` | Real local server persistence, transactions, search, snapshot roundtrips and CLI; independent uv project |

```sh
uv run check
uv run check --all
# One Python module, or the entire tooling suite
uv run python -m unittest tests.tooling.test_map_validation -v
uv run python -m unittest discover -s tests/tooling -t . --buffer --durations 5
# Knowledge graph suites (separate Linux CI job; isolated servers, no API keys)
uv run --locked --project tools/kg python -m unittest discover -s tools/kg/tests --buffer
uv run --locked --project tools/kg python -m unittest discover -s knowledge/tests --buffer
# After check has refreshed engine references
node tests/run.cjs battles
node tests/run.cjs presentation
```

`run.cjs` runs `battles`, `gameplay` and `presentation` in isolated Ruby WASM VMs.
Gameplay loads every custom script in archive order with real Essentials Pokémon,
bag and SaveData objects. Custom Ruby must support the native Ruby 3.1 runtime;
WASM uses Ruby 3.2. Battle execution and display are doubles, so headless checks
cannot establish real battle-engine behavior, rendering, scheduling or audio.

`prepare_reference.py` extracts `game/Data/Scripts.rxdata` into ignored
`engine_reference/`; never edit that extraction. The harness selects stock scripts
by name, since numeric prefixes change with archive order. `check` supplies fresh
map-event bodies. Put doubles in `support/`; quest regressions belong in the full
gameplay suite, not partial source evals.

## What earns a test

Test an observable player or maintainer failure through the operation that causes
it: lost identity/items, stuck progression, invalid arrival, partial publication,
wrong release inputs or saves in the wrong namespace. Extend the existing harness
and shared fixtures. Mock an external service when needed, never the operation under test.

Do not add import-only checks, source/YAML substring assertions, copied catalog
values, or another platform copy of shared pipeline tests. `check --all` owns
whole-tree regeneration/pixel parity. Native scenarios own real engine/platform
claims. Cover the shared quest path once; vary choices where behavior changes.
Test count and coverage percentage are not targets.

## Native verification

Use [releasing](../docs/releasing.md) for packaging and platform commands. Each
launcher accepts `--scenario runtime|world|species|all` (default `all`). Use a
package from the same checkout as its PBS and test sources.

- `runtime` checks initialization, a real save roundtrip, a rendered font/sprite
  and resizing at small, large, wide and tall window sizes while preserving the
  logical game canvas. Desktop checks must still verify the final scaled image
  and fullscreen transitions.
- `world` uses [declared starts](../docs/development.md#playtest-scenarios) to capture
  home, coast, forest, lighthouse, vault, docks and pond. It checks companion/item/
  quest continuity, stale-map refresh, state before map callbacks and interrupted
  forced-route restoration. Seven scenes are not a complete walkthrough.
- `species` recompiles PBS with native Essentials and compares custom species and
  metrics, excluding PBS bookkeeping and non-evolving family backlinks. Its
  catalog-derived `NativeContent` fixture checks exact normal/shiny sprites,
  icons and cries, plus story item and trainer artwork. Base/placeholder fallback
  cannot satisfy required artwork.

Fixtures replace Main and isolate saves only in disposable players, then clean
up their own save directories. Never put a test driver in `src/load_order.txt`,
modify a release archive or alter player saves to set up a test. The developer
CLI smoke check also verifies development save isolation.

Mac CI runs one read-only App Translocation launch per architecture; additional
`--location` diagnostics are opt-in. Windows launches from a relocated Unicode
path; Linux also checks a symlink launcher and read-only game tree under Xvfb.
Evidence includes `native-smoke.json`, logs and PNGs. Desktop audio, hardware-GPU
behavior, controls and complete gameplay remain separate manual checks. For quest
changes, report the retry/cancel/transfer interactions actually played.

PR pushes run quick checks. Use `/verify` for the full native workflow. Do not add
platform/path matrices per feature or run native builds for prose-only changes.
