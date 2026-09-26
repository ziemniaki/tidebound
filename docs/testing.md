# Testing

Run `uv run check` for the normal headless gate. It checks tooling regressions,
map/source agreement, geometry and Ruby domain/native-object suites without
rewriting tracked game data. `uv run check --all` additionally regenerates in a
disposable copy and compares binary data and decoded PNG pixels. Stage new source
files first so the tracked-file copy includes them.

## Coverage

| Check | What it establishes |
| --- | --- |
| Python `test_*.py` | Packaging safety, provenance, failure cleanup, workflow authorization and developer commands |
| `tests/run.cjs` | Domain and battle-adapter rules with test doubles |
| `tests/native_domain.cjs` | Actual Essentials Pokémon, owner, bag and SaveData objects; all starters, quest branches, retries and old-save migration |
| `tests/regional_snakes.cjs` | Native species/forms, move inheritance, evolution and save preservation |
| Geometry checks | Walkable arrivals/interactions, maze routes and Surf-only pond island |
| Native platform smoke | Packaged engine startup, compiled data, actual save roundtrip, graphics/fonts and input initialization |

`check` obtains the locked Node packages automatically. For individual harnesses,
run from the repository root after setup:

```sh
uv run python tests/prepare_reference.py
node tests/run.cjs
node tests/native_domain.cjs
node tests/regional_snakes.cjs
```

`tests/engine_reference/` is an ignored extraction of the current archive. It is
not editable source. The shared VM harness resolves stock scripts by name and
loads complete scripts. Integration scenarios load every custom archive entry in
production order before exercising story flows. Engine/display services are
explicit test fixtures; production modules are never split at comments or scraped
into partial definitions. Prefer the complete `check`
gate, which supplies fresh event scripts instead of relying on a stale report.
Custom Ruby must remain compatible with the bundled Ruby 3.1 runtime, even though
the Node harness uses Ruby 3.2 WASM.

## Native builds

Use the [release guide](releasing.md) for exact archive smoke commands. Mac tests
run on Intel and ARM in ordinary, temporary, Downloads, long Unicode and actual
read-only App Translocation locations. Windows starts a relocated Unicode-named
package from outside its game folder. Linux adds a symlink launcher and read-only
game tree on Ubuntu 22.04/24.04.

Native fixtures replace Main and isolate saves only in disposable copies. Never
embed a test driver into release data. The shipped archive remains unchanged.
The developer-workflow check also builds a local player and verifies its separate
save configuration. Real desktop audio, hardware graphics, controls and complete
gameplay remain manual checks; record them separately from smoke results.

Older feature-specific Ruby drivers and [historical reports](history/README.md)
remain useful references. Some use old coordinates or require retained save
fixtures; they are not all part of the current automatic gate.
