# Essentials baseline

`base.zip` is the offline input for the generated RPG Maker project. `base.json`
pins its SHA-256 and source commit. Builds verify the archive before replacing
outputs; runtime player executables remain in their existing platform archives.

This is a **curated snapshot of the project's Essentials 21.1 inputs**, taken from
Tidebound commit `af9ecdbc2a88786c3e9c1d5e6533415ef5a07e85`, not a pristine upstream
Essentials download. Existing stock content and historical engine adaptations
are preserved. Attribution remains in [credits](../../docs/credits.md).

The extraction excluded `game/AGENTS.md`, `.generated/`, owned asset/file outputs
listed by that commit's asset/content inventories, and custom database records
listed by its content inventory. Authored tileset slots were cleared; trailing
empty slots were removed. Tidebound script entries were removed and the three
literal engine patches were reversed; the build reapplies its explicit patches.
Generated map-metadata PBS sections were removed. Launch configuration,
System/start state and global metadata moved to `content/overrides/`.

Native species/item/trainer record values are unchanged after assembly; Marshal
hash insertion order can differ because custom records are appended to the base.
Map IDs, tile positions, stock paths and save identities are retained.

Game changes belong in `src/`, authored content bundles or native overrides.
For an intentional engine update, review a new baseline's provenance and contents,
update the archive and pin together, then run `uv run check --all` and full native
verification. Never create a new baseline by archiving a generated `game/`.
