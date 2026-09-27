# Verification boundaries

Run commands from the repository root. `uv run check` prepares locked Node packages,
extracts the current archive and supplies fresh map-event scripts to the harness.
It does not rebuild source. Format and embed Ruby first; content/map edits need
full regeneration before checking. `check --all` copies only Git-tracked paths:
stage new files before running it.

## Pick the engine boundary being tested

- `run.cjs` covers domain/adapters with doubles. `native_domain.cjs` loads real
  Essentials data objects plus the complete custom script composition. Add quest
  regressions to the matching Ruby flow via this harness, not a partial file eval
  that omits later hooks. `support/ruby_vm.cjs` selects stock scripts by name;
  extraction numeric prefixes change when archive entries change.
- `prepare_reference.py` refreshes ignored `engine_reference/` from
  `game/Data/Scripts.rxdata`. Editing that directory fixes neither production nor
  the next check. Do not use it as a second source tree.
- Engine doubles are explicit in `support/`. A double can establish a state
  transition; it cannot establish real event scheduling, sprite ownership, sound,
  or native platform behavior. Do not stub away the engine operation under test.
- For species, `native_scenarios.rb` consumes the catalog-derived `NativeContent`
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
