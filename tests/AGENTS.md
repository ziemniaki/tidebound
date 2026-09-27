# Verification boundaries

Run commands from the repository root. `uv run check` prepares locked Node packages,
extracts the current archive and supplies fresh map-event scripts to the harness.
It assembles the native project before checking; no committed game outputs are needed. `check --all` copies only Git-tracked paths:
stage new files before running it.

## What earns a test

Keep a regression when it names a player or maintainer failure and exercises the
operation that can cause it: lost identity/items, stuck progression, invalid map
arrival, partial publication, wrong release inputs, or saves written to the wrong
namespace. Assert the observable result. A mock of the failing external service
is useful; mocking the operation under test is not.

Do not add import-only checks, source/YAML substring assertions, copied catalog
values, or another platform copy of shared pipeline tests. `check --all` owns
whole-tree regeneration/pixel parity. Native scenarios own real engine/platform
claims. One end-to-end quest covers the shared path; vary choices only where they
change behavior. A test count or coverage percentage is not a target.

## Pick the engine boundary being tested

- `tooling/` uses standard Python `unittest`; `gameplay/` contains Ruby scenarios.
  `run.cjs` runs `battles`, `gameplay` and `presentation` in isolated VMs. The
  gameplay suite loads real Essentials data objects and every custom script in
  archive order. Add quest regressions there, never to partial source evals.
  `support/ruby_vm.cjs` selects stock scripts by name; numeric extraction prefixes
  change whenever archive entries change. Put doubles in `support/`, not scenarios.
- `prepare_reference.py` refreshes ignored `engine_reference/` from
  `game/Data/Scripts.rxdata`. Editing that directory fixes neither production nor
  the next check. Do not use it as a second source tree.
- Engine doubles are explicit in `support/`. A double can establish a state
  transition; it cannot establish real event scheduling, sprite ownership, sound,
  or native platform behavior. Do not stub away the engine operation under test.
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

Keep quick checks on PR pushes. Use existing native `runtime|world|species`
scenarios for relevant integration work, `/verify` for full platform evidence.
Do not add a platform/path matrix for each feature or run expensive builds for
prose-only changes. Commands: [testing](../docs/testing.md).
