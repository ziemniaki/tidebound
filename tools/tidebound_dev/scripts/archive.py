"""Shared checks for the single embedded Tidebound loading path."""

import zlib

from rubymarshal.reader import loads


def script_name(value):
    return value.decode("utf-8") if isinstance(value, bytes) else str(value)


def reject_plugin_copy(game):
    if (game / "Plugins/Tidebound").exists():
        raise ValueError(
            "Remove Plugins/Tidebound: custom scripts must load only from Data/Scripts.rxdata."
        )


def source_name(path, source_root):
    name = path.relative_to(source_root).with_suffix("").as_posix()
    return "Tidebound/" + name.removeprefix("tidebound/")


def source_files(source_root):
    manifest = source_root / "load_order.txt"
    if not manifest.is_file():
        raise ValueError(f"Missing source manifest: {manifest}")
    names = [
        line.strip()
        for line in manifest.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not names or len(names) != len(set(names)):
        raise ValueError("Source manifest must list every file exactly once")
    files = []
    for name in names:
        path = source_root / name
        if (
            path.suffix != ".rb"
            or not path.resolve().is_relative_to(source_root.resolve())
            or not path.is_file()
        ):
            raise ValueError(f"Missing or invalid source manifest entry: {name}")
        files.append(path)
    if set(files) != set(source_root.rglob("*.rb")):
        raise ValueError(
            "Source manifest must list every Ruby source exactly once; unlisted files found"
        )
    if len({source_name(path, source_root) for path in files}) != len(files):
        raise ValueError("Source manifest produces duplicate archive names")
    return files


def validate_archive(game, dev):
    """Check entries before indexing: a dict would hide duplicate executions."""
    reject_plugin_copy(game)
    files = source_files(dev)
    entries = loads((game / "Data/Scripts.rxdata").read_bytes())
    names = [script_name(entry[1]) for entry in entries]
    if names.count("Main") != 1:
        raise ValueError("Script archive must contain exactly one Main entry")
    expected = [source_name(path, dev) for path in files]
    actual = [name for name in names if name.startswith("Tidebound/")]
    if actual != expected:
        raise ValueError(
            "Tidebound entries must match manifest sources exactly once, in manifest order"
        )
    main = names.index("Main")
    if names[max(0, main - len(expected)) : main] != expected:
        raise ValueError("Tidebound entries must be contiguous immediately before Main")
    scripts = {
        script_name(entry[1]): zlib.decompress(entry[2]).decode("utf-8-sig") for entry in entries
    }
    for path in files:
        if scripts[source_name(path, dev)] != path.read_text(encoding="utf-8"):
            raise ValueError(
                f"Embedded source differs from {path.name}; run uv run build --compile-only"
            )
    if scripts["Main"].count("Scene_TideboundTitle") != 1:
        raise ValueError("Main must launch Scene_TideboundTitle exactly once")
    return scripts
