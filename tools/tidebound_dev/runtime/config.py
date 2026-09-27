"""mkxp configuration and save identities shared by players and disposable fixtures."""

import json
import re

SAVE_DIRECTORY = "Tidebound_Opening_0_2"
DEV_SAVES = "Tidebound_Development"
PLAYTEST_SAVES = "Tidebound_Playtest"


def parse_runtime_config(text):
    """Parse mkxp JSON comments without treating quoted URLs as comments."""
    tokens = r'"(?:\\.|[^"\\])*"|//[^\r\n]*|/\*[\s\S]*?\*/'
    text = re.sub(tokens, lambda m: m[0] if m[0].startswith('"') else " ", text)
    # mkxp accepts trailing commas as well as comments. Skip quoted strings so
    # literal comma/brace text in paths or window titles is never rewritten.
    text = re.sub(
        r'"(?:\\.|[^"\\])*"|,\s*(?=[}\]])', lambda m: m[0] if m[0].startswith('"') else "", text
    )

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate runtime configuration key: {key}")
            result[key] = value
        return result

    config = json.loads(text, object_pairs_hook=unique)
    if not isinstance(config, dict):
        raise ValueError("Expected a runtime configuration object")
    return config


def isolated_saves(text, namespace):
    """Rewrite only a disposable player's settings, using mkxp's actual JSON rules."""
    try:
        config = parse_runtime_config(text)
    except ValueError as error:
        raise ValueError(f"Expected exactly one save namespace setting: {error}") from error
    if not isinstance(config.get("dataPathApp"), str):
        raise ValueError("Expected exactly one save namespace setting")
    config["dataPathApp"] = namespace
    return json.dumps(config, indent=2, ensure_ascii=False) + "\n"
