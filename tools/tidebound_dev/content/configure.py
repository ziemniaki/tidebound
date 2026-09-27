"""Write authored map metadata alongside stock PBS sections."""

from ..maps import definitions
import json
import re


def build(root):
    GAME = root / "game"
    by_id = {d.id: d for d in definitions.load(root).values()}
    # Read required generator output before changing editor metadata.
    manifest = json.loads((GAME / ".generated/map_manifest.json").read_text())
    p = GAME / "PBS/map_metadata.txt"
    s = p.read_text(encoding="utf-8-sig")
    s = s.split("# TIDEBOUND OPENING MAPS")[0]
    # Adopting a native map also replaces its existing PBS section. Essentials
    # rejects duplicate IDs when it recompiles the editor project.
    s = re.sub(
        r"(?ms)^\[(\d+)\][^\n]*\n.*?(?=^\[|\Z)",
        lambda section: "" if int(section[1]) in by_id else section[0],
        s,
    )
    s = s.rstrip() + "\n\n# TIDEBOUND OPENING MAPS\n"
    for m in manifest:
        s += f"#-------------------------------\n[{m['id']}]\n"
        for key, value in by_id[m["id"]].pbs_metadata(m["name"]).items():
            value = str(value).lower() if isinstance(value, bool) else value
            s += f"{key} = {value}\n"
    p.write_text(s, encoding="utf-8-sig")
    print("Updated authored map metadata PBS.")
