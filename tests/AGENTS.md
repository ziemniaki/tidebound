# Verification boundaries

`uv run check` prepares locked Node packages, assembles the native project,
extracts its archive and supplies fresh map-event scripts to the harness.
No committed game outputs are needed. Stage new sources before `check --all`:
its isolated build copies only Git-tracked paths.

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

## Pick the engine boundary being tested

- `tooling/` uses standard Python `unittest`; `gameplay/` contains Ruby scenarios.
  `run.cjs` runs `battles`, `gameplay` and `presentation` in isolated VMs. The
  gameplay suite loads real Essentials data objects and every custom script in
  archive order. Add quest regressions there, never to partial source evals.
  `support/ruby_vm.cjs` selects stock scripts by name; numeric extraction prefixes
  change whenever archive entries change. Put doubles in `support/`, not scenarios.
- `prepare_reference.py` refreshes ignored `engine_reference/` from
  `game/Data/Scripts.rxdata`; it is an inspection copy, never an editable source.
- Engine doubles are explicit in `support/`. A double can establish a state
  transition; it cannot establish real event scheduling, sprite ownership, sound,
  or native platform behavior.
- For species, `native/native_scenarios.rb` consumes the catalog-derived `NativeContent`
  fixture and compares native attributes/metrics before and after real PBS
  compilation. It checks exact sprite/icon/cry resolution, so a bitmap returned
  through fallback to `000` cannot pass required-art verification.
- Native fixtures replace Main and isolate saves only in disposable players.
  Never place their driver in `src/load_order.txt` or edit player saves to set up a
  test. A package and its checkout/PBS inputs must represent the same changes.
- `world` captures seven named scenes and a save/load roundtrip; it is not a full
  walkthrough. When changing a quest, test its retry/cancel/transfer behavior and
  report separately which interactions were actually played.

Use existing native `runtime|world|species` scenarios for integration, `/verify`
for full platform evidence. Keep quick checks on PR pushes; do not add per-feature
platform/path matrices or expensive prose-only builds. Commands: [testing](../docs/testing.md).
