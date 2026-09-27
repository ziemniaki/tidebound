"""Prepare disposable native fixtures without touching player data or source archives."""

from pathlib import Path
import re
import shutil
import zlib

from rubymarshal.reader import loads
from rubymarshal.writer import writes
from tidebound_dev.runtime.config import isolated_saves
from tidebound_dev.content.verification import inventory
from tidebound_dev import scenarios

SCENARIOS = ("runtime", "world", "species", "all")


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
        driver += b"\n" + (tests / "development_scenarios.rb").read_bytes()
        root = tests.parent.parent
        specs = [scenarios.select(root, name) for name in scenarios.catalog(root)]
        (game / "NativeScenarios.rxdata").write_bytes(writes(specs))
    driver += b"\n" + (tests / "native_runtime_smoke.rb").read_bytes()
    main[0][2] = zlib.compress(driver)
    # Validate both files before publishing either change in this disposable copy.
    encoded = writes(entries)
    if scenario in ("species", "all"):
        shutil.copytree(tests.parent.parent / "game/PBS", game / "NativePBS")
        (game / "NativeContent.rxdata").write_bytes(writes(inventory()))
    config.write_text(text, encoding="utf-8")
    scripts.write_bytes(encoded)
