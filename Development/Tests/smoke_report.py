"""Decode native smoke evidence without requiring Ruby's optional JSON library."""
import json
from rubymarshal.classes import RubyString
from rubymarshal.reader import loads


def read_report(output):
    def plain(value):
        if isinstance(value, RubyString):
            return str(value)
        if isinstance(value, dict):
            return {plain(key): plain(item) for key, item in value.items()}
        if isinstance(value, list):
            return [plain(item) for item in value]
        return value

    result = plain(loads((output / 'native-smoke.rxdata').read_bytes()))
    (output / 'native-smoke.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result
