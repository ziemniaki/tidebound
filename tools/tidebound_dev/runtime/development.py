"""Replace the entry point only in a staged development player."""

import zlib
from rubymarshal.reader import loads
from rubymarshal.writer import writes


def replace_main(game, driver):
    path = game / "Data/Scripts.rxdata"
    entries = loads(path.read_bytes())
    mains = [entry for entry in entries if entry[1] == "Main"]
    if len(mains) != 1:
        raise ValueError("Development player requires exactly one Main entry")
    mains[0][2] = zlib.compress(driver)
    path.write_bytes(writes(entries))
