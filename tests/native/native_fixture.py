"""Prepare isolated native fixtures and decode their evidence on every platform."""

from pathlib import Path
import json
import re
import shutil
import zlib

from rubymarshal.classes import RubyString
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from tidebound_dev.runtime.config import isolated_saves
from tidebound_dev.content.species_compiler import SPECIES, METRICS, identity
from tidebound_dev import scenarios

SCENARIOS = ("runtime", "world", "species", "all")


def inventory():
    # Include each form's base so compiler-added family relationships are checked.
    species = sorted(set(SPECIES) | {identity(name)[0] for name in SPECIES})
    art = []
    for identifier in SPECIES:
        name, form = identity(identifier)
        art.append(
            {
                "id": identifier,
                "species": name,
                "form": form,
                "front": f"Graphics/Pokemon/Front/{identifier}.png",
                "back": f"Graphics/Pokemon/Back/{identifier}.png",
                "front_shiny": f"Graphics/Pokemon/Front shiny/{identifier}.png",
                "back_shiny": f"Graphics/Pokemon/Back shiny/{identifier}.png",
                # The current art direction shares normal and shiny party icons.
                "icon": f"Graphics/Pokemon/Icons/{identifier}.png",
                "icon_shiny": f"Graphics/Pokemon/Icons/{identifier}.png",
                "cry": f"Cries/{identifier}",
            }
        )
    return {"species": species, "metrics": sorted(METRICS), "art": art}


def prepare(game, namespace, scenario="all"):
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown native scenario: {scenario}")
    if not re.fullmatch(r"Tidebound_Build_Smoke_[a-f0-9]{32}", namespace):
        raise ValueError("Native fixtures require a unique test namespace")
    config = game / "mkxp.json"
    text = isolated_saves(config.read_text(encoding="utf-8"), namespace)
    scripts = game / "Data/Scripts.rxdata"
    entries = loads(scripts.read_bytes())
    main = [entry for entry in entries if entry[1] == "Main"]
    if len(main) != 1:
        raise ValueError("Expected exactly one Main entry")
    tests = Path(__file__).parent
    driver = f"TIDEBOUND_NATIVE_SCENARIO = :{scenario}\n".encode()
    driver += (tests / "native_scenarios.rb").read_bytes()
    if scenario in ("world", "all"):
        driver += b"\n" + Path(scenarios.__file__).with_suffix(".rb").read_bytes()
        root = tests.parent.parent
        (game / "NativeStart.rxdata").write_bytes(writes(scenarios.select(root, "neighbor/meal")))
        (game / "NativePond.rxdata").write_bytes(
            writes(json.loads((root / "content/maps/road/mechanics.json").read_text()))
        )
    driver += b"\n" + (tests / "native_runtime_smoke.rb").read_bytes()
    main[0][2] = zlib.compress(driver)
    # Validate both files before publishing either change in this disposable copy.
    encoded = writes(entries)
    if scenario in ("species", "all"):
        shutil.copytree(tests.parent.parent / "game/PBS", game / "NativePBS")
        (game / "NativeContent.rxdata").write_bytes(writes(inventory()))
    config.write_text(text, encoding="utf-8")
    scripts.write_bytes(encoded)


def read_report(output):
    def plain(value):
        # Ruby exceptions can be ASCII-8BIT strings even when their message is
        # UTF-8. Preserve the failure instead of hiding it behind a JSON error.
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        if isinstance(value, RubyString):
            return str(value)
        if isinstance(value, dict):
            return {plain(key): plain(item) for key, item in value.items()}
        if isinstance(value, list):
            return [plain(item) for item in value]
        return value

    result = plain(loads((output / "native-smoke.rxdata").read_bytes()))
    (output / "native-smoke.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result
