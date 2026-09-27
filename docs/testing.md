# Testing

Run `uv run check` for the normal headless gate. It checks Python/Ruby formatting, tooling regressions,
map/source agreement, geometry and Ruby domain/native-object suites without
rewriting tracked game data. `uv run check --all` additionally regenerates in a
disposable copy and compares binary data and decoded PNG pixels. Stage new source
files first so the tracked-file copy includes them.

## Test suites

| Location | What it protects |
| --- | --- |
| `tests/tooling/` | Generator dependencies, generated-map reachability, archive safety, release provenance and save isolation |
| `tests/gameplay/` | Companion identity, battle rollback, quest progression/retries, real Essentials saves and resource ownership |
| `tests/native/` | Packaged runtime startup, graphics, actual engine saves and platform path handling |
| `tests/support/` | Explicit engine doubles and shared headless setup |

Python's standard `unittest` runs the tooling suite. Ruby scenarios run through
one Node launcher using the pinned Ruby WASM runtime. Its three suites each get
a fresh VM; compilation is shared, globals are not. Gameplay loads the complete
embedded custom scripts with actual Essentials Pokémon, bag and SaveData objects.
Display and battle execution remain doubles, so these checks cannot prove rendering
or real battle-engine behavior. Native tests cover that separate runtime boundary.

```sh
# One tooling module (no Node startup)
uv run python -m unittest tests.tooling.test_map_validation -v
# All tooling checks; successful tool output is hidden, failures retain it
uv run python -m unittest discover -s tests/tooling -t . --buffer --durations 5
# One isolated Ruby suite, after a successful check has refreshed engine references
node tests/run.cjs battles
node tests/run.cjs presentation
```

`uv run check` also validates maps and supplies fresh event bodies to the gameplay
suite. Use it for quest/event changes. `tests/engine_reference/` is an ignored
extraction of the current archive, never editable source. The harness selects stock
scripts by name and custom scripts in archive order. Custom Ruby must remain
compatible with bundled Ruby 3.1; WASM uses Ruby 3.2.

Full artwork parity belongs to `check --all`, which regenerates once and compares
decoded pixels. Focused asset tests cover alpha preservation, required shiny inputs, character/icon
formats, stale-output removal and lighting through tileset packing.

## Native builds

Use the [release guide](releasing.md) for exact archive smoke commands. Mac tests
run one actual read-only App Translocation launch on Intel and one on ARM.
Other locations are available with `--location`; `--location all` is an opt-in
diagnostic for runtime path changes. Windows starts a relocated Unicode-named
package from outside its game folder. Linux adds a symlink launcher and read-only
game tree on Ubuntu 22.04/24.04.

Native fixtures replace Main and isolate saves only in disposable copies. Never
embed a test driver into release data. The shipped archive remains unchanged.
The developer-workflow check also builds a local player and verifies its separate
save configuration. Real desktop audio, hardware graphics, controls and complete
gameplay remain manual checks; record them separately from smoke results.

## Native scenarios

The platform launchers accept `--scenario runtime|world|species|all` (default
`all`). They prepare a disposable player from a package, replace only its Main
entry, assign a unique save namespace and remove the test saves afterward.
No existing player save or manually prepared engine directory is required.

```sh
uv run python -m tests.native.mac_runtime_smoke /path/to/Tidebound_Mac_0.8.8_universal.zip /tmp/tidebound-scenes --arch arm64 --location ordinary --scenario world
uv run python -m tests.native.windows_runtime_smoke C:/build/Tidebound_Windows_0.8.8_x64.zip C:/build/scenes --scenario all
uv run python -m tests.native.linux_runtime_smoke /tmp/Tidebound_Linux_0.8.8_x86_64.zip /tmp/tidebound-scenes --scenario all
```

`runtime` exercises initialization and native save roundtrips. `world`
starts through the same `play --from` bootstrap, then captures home, coast, forest,
lighthouse, vault, docks and pond. One native save/load checks companion identity,
held items, quest state and stale-map refresh; it also verifies state exists before
map callbacks and that interrupting a forced route restores the actor. `species` recompiles the
current checkout's PBS with Essentials in the isolated save directory, compares all custom species and metric attributes (excluding PBS provenance and
non-evolving family backlinks), and checks exact normal/shiny front/back/icon/cry
paths. Its roster is derived from authored catalogs; deliberate cry/icon reuse is
declared once in `art/pokemon.py`. Custom story item icons and trainer portraits/charsets also resolve explicitly.
Missing art cannot pass through base or placeholder fallback. Use a
package built from the same checkout. Linux CI runs under Xvfb.

Evidence includes `native-smoke.json`, engine logs and PNG captures.
Full CI runs the portable headless gate once on Linux. Mac path-resolver checks
run in the packaging job; native player launches retain their platform coverage.
