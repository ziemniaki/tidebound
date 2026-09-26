# Repository layout and development workflow

## Findings

The previous root was also the engine's working directory. It mixed game data,
executables, player instructions, release notes and project handoffs. `Development/`
combined custom Ruby, map/data authoring, build tools, tests, source art, the game
bible and generated reports. Its purpose did not tell a new contributor where
to make a change.

The 96 KB `AGENTS.md` repeated release history and superseded instructions:
ZIP-only logistics coexisted with GitHub workflows, and the old Mac installation
workaround remained beside its fix. The README mixed onboarding with changelog
and verification history. Python setup required manual environment commands,
while local players had no common build/launch command.

## Decisions

- Keep the engine's conventional layout intact inside `game/`; keep custom Ruby
  in `src/`. Generators/build automation live in `tools/`, tests in `tests/`, and
  original art/recipes in `assets/`.
- Put the main specification and species/quest specifications in `specs/`.
  Put operational, platform, art and runtime documentation in `docs/`.
- Keep a small root `AGENTS.md` that routes agents to authoritative sources and
  states invariants. The refactoring supersedes the archive-in-tree policy: preserve old records in Git history, explicitly
  marked historical; do not silently delete accepted creative decisions.
- Write the README for a first-time visitor: what the game is, a real screenshot,
  a play link, a short development quickstart, navigation, help and attribution.
  Detailed instructions belong in linked documentation. This follows
  [GitHub's README guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes).
- Use [uv project entry points](https://docs.astral.sh/uv/concepts/projects/config/)
  for `play`, `build`, `check`, `rebuild`, `doctor` and `editor`. Commit the Python
  lockfile and use it in [GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/).
  Ordinary play/build does not need Node; checks manage its locked test packages.
- Restore Windows binaries automatically from pinned, offline-capable archives.
  Ignore loose binaries, caches and local builds. Repacking does not erase large
  files from Git history; external hosting/LFS is a separate migration.
- Use separate development saves and a distinct Mac bundle identifier, so local
  playtesting cannot overwrite a released app or its normal save files.
- Defer [devenv](https://devenv.sh/getting-started/): Nix/WSL2 adds a second setup
  layer and does not cover the native Windows editor. Revisit if system-tool
  drift becomes a concrete problem; the present commands work on native hosts.

## Scope and verification

The migration preserves numbered Ruby source, compiled scripts/maps, assets and
runtime binary contents. Generated PBS comments now name the relocated tools.
It does not redesign the map format, quest model, save schema or engine.

Validation includes headless suites, isolated regeneration, all three packagers,
native runtime tests, and the developer command on Mac Intel/ARM, Windows and
Linux CI hosts. Full CI stays on demand; quick PR checks do not build players.
Use the PR's exact-head run for completed results rather than treating this
description as evidence that a run has passed.
