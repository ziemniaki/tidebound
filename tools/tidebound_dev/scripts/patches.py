"""The four intentional adaptations to stock Essentials source during embedding."""
import re
import zlib

from tidebound_dev.scripts.archive import script_name


LITERAL_PATCHES = {
    'Battler_ChangeSelf': ('"{1} fainted!"', '"{1} died!"'),
    'Overworld': ('"{1} fainted..."', '"{1} died..."'),
    'Main': ('return Scene_Intro.new', 'return Scene_TideboundTitle.new'),
}


def replace_setting(code, pattern, replacement):
    updated, count = re.subn(pattern, replacement, code)
    if count != 1:
        raise ValueError(f'Expected one engine setting matching {pattern}')
    return updated


def patch_engine(entries, version):
    """Return patched entries, rejecting unsupported engine changes before writing."""
    required = {'Settings', *LITERAL_PATCHES}
    for name in required:
        if sum(script_name(entry[1]) == name for entry in entries) != 1:
            raise ValueError(f'Expected exactly one stock engine script: {name}')
    result = []
    for identifier, raw_name, compressed in entries:
        name = script_name(raw_name)
        if name in required:
            code = zlib.decompress(compressed).decode('utf-8-sig')
            if name == 'Settings':
                code = replace_setting(code, r'GAME_VERSION = "[^"]+"', f'GAME_VERSION = "{version}"')
                code = replace_setting(code, r'TIME_SHADING\s*=\s*(?:true|false)', 'TIME_SHADING = false')
            else:
                original, replacement = LITERAL_PATCHES[name]
                if code.count(original) + code.count(replacement) != 1:
                    raise ValueError(f'Unsupported engine patch target: {name}')
                code = code.replace(original, replacement)
            compressed = zlib.compress(code.encode('utf-8'), 9)
        result.append([identifier, name, compressed])
    return result
