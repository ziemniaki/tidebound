"""Shared checks for the single embedded Tidebound loading path."""
import zlib

from rubymarshal.reader import loads


def script_name(value):
    return value.decode("utf-8") if isinstance(value, bytes) else str(value)


def reject_plugin_copy(game):
    if (game / "Plugins/Tidebound").exists():
        raise ValueError("Remove Plugins/Tidebound: custom scripts must load only from Data/Scripts.rxdata.")


def source_files(dev):
    files = sorted(dev.glob("[0-9][0-9][0-9]_*.rb"))
    if not files:
        raise ValueError(f"No numbered Ruby sources found in {dev}")
    return files


def validate_archive(game, dev):
    """Check entries before indexing: a dict would hide duplicate executions."""
    reject_plugin_copy(game)
    files = source_files(dev)
    entries = loads((game / "Data/Scripts.rxdata").read_bytes())
    names = [script_name(entry[1]) for entry in entries]
    if names.count("Main") != 1:
        raise ValueError("Script archive must contain exactly one Main entry")
    expected = ["Tidebound/" + path.stem for path in files]
    actual = [name for name in names if name.startswith("Tidebound/")]
    if actual != expected:
        raise ValueError("Tidebound entries must match numbered sources exactly once, in filename order")
    main = names.index("Main")
    if names[max(0, main - len(expected)):main] != expected:
        raise ValueError("Tidebound entries must be contiguous immediately before Main")
    scripts = {script_name(entry[1]): zlib.decompress(entry[2]).decode("utf-8-sig")
               for entry in entries}
    for path in files:
        if scripts["Tidebound/" + path.stem] != path.read_text(encoding="utf-8"):
            raise ValueError(f"Embedded source differs from {path.name}; run Development/rebuild_scripts.py")
    if scripts["Main"].count("Scene_TideboundTitle") != 1:
        raise ValueError("Main must launch Scene_TideboundTitle exactly once")
    return scripts
