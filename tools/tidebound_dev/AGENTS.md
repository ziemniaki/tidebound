# Authoring and build tools

Follow the [development workflow](../../docs/development.md) and
[runtime boundaries](../../docs/architecture.md#runtime-boundaries).
Read the affected content guide from the [task table](../../AGENTS.md#read-for-your-change);
exported assets also use [art/AGENTS.md](art/AGENTS.md).

- Extend this installed Python package. `cli.py` owns parsing and aliases;
  `pipeline.py` owns rebuild order. Commands and CI call the same operations.
  Do not add standalone generator chains, `sys.path` patches or a second CLI path.
- Put reusable operations with their owner; the CLI only coordinates them.
  Formatting owns its dependency setup; operations must not import it from the CLI.
- Compilers/exporters accept explicit roots so the same code works in the checkout
  and isolated regeneration. Do not hardcode a developer's paths or read outputs
  from another checkout.
- Extend existing declarations, discovery and ownership records together. Derive
  output paths and checks from the same catalog; do not add parallel registration
  lists. Generated files are outputs, never recipe inputs or manual fixes.
- Preserve dependency order, stock inputs and editor import safeguards. Failed
  builds require fixing the source and rerunning, not bypassing validation or
  deleting checkpoints. See the [editor workflow](../../docs/development.md#rpg-maker).
- Keep shared staging in `packaging/pipeline.py`; platform adapters own layout,
  signing and permissions. Follow [releasing](../../docs/releasing.md) for release work.

Verify observable behavior through the existing [test boundaries](../../tests/AGENTS.md).
For compilation/export changes, rebuild, stage new sources/outputs and run
`uv run check --all` to prove isolated regeneration. Update the documented command
or workflow when its behavior changes.
