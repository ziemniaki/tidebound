"""Stage native players once; archive only release candidates."""

from pathlib import Path
import json
import re
import shutil
import subprocess
import sys
import tempfile

from tidebound_dev.release.metadata import (
    ROOT,
    SAVE_DIRECTORY,
    check_sources,
    sha256,
    source_revision,
)
from tidebound_dev.maps.validate import validate
from . import linux, mac, windows
from .archives import archive_tree, copy_game, copy_verified, extract_bundle, game_hashes

PLATFORMS = {"mac": mac, "windows": windows, "linux": linux}
DEV_SAVES = "Tidebound_Development"


def development_settings(game):
    path = game / "mkxp.json"
    text, count = re.subn(
        r'("dataPathApp"\s*:\s*)"[^"]+"',
        lambda match: match[1] + json.dumps(DEV_SAVES),
        path.read_text(encoding="utf-8"),
    )
    if count != 1:
        raise ValueError(
            "Expected exactly one save directory setting; refusing unsafe development build"
        )
    path.write_text(text, encoding="utf-8")


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def stage_player(folder, platform, root, config, development=False):
    """All modes use the same runtime, payload and platform finalization."""
    adapter = PLATFORMS[platform]
    folder.mkdir()
    player = adapter.prepare(folder, root, config, development)
    copy_game(root / "game", player.game)
    copy_verified(root / "docs/credits.md", folder / "CREDITS.md")
    copy_verified(root / f"docs/players/{platform}.txt", folder / "README.txt")
    if development:
        development_settings(player.game)
    adapter.finalize(player)
    return player


def build(platform, output, root=ROOT, allow_dirty=False, development=False):
    """Publish a complete player or verified ZIP atomically; preserve existing output."""
    output = output.resolve()
    if output.exists():
        raise FileExistsError(
            "Choose a new output directory; existing builds are never overwritten"
        )
    config = check_sources(root)
    revision = source_revision(root, allow_dirty)
    validate(root)
    adapter = PLATFORMS[platform]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".tidebound-package-", dir=output.parent) as temp:
        artifacts = Path(temp) / "artifacts"
        artifacts.mkdir()
        folder = artifacts / f"Tidebound_{adapter.NAME}_{config['version']}_{adapter.ARCHITECTURE}"
        player = stage_player(folder, platform, root, config, development)
        if development:
            result = output / folder.name / player.launcher.relative_to(folder)
            write_json(
                folder / "DEVELOPMENT.json",
                {
                    "kind": "development",
                    "platform": platform,
                    "save_directory": DEV_SAVES,
                    "launcher": str(result),
                    "source_commit": revision["commit"],
                },
            )
        else:
            manifest = {
                "version": config["version"],
                "source": revision,
                "save_directory_name": SAVE_DIRECTORY,
                **player.metadata,
            }
            hash_key = "game_sha256" if platform == "mac" else "files_sha256"
            manifest[hash_key] = game_hashes(player.game, "NFC" if platform == "mac" else None)
            write_json(folder / "BUILD.json", manifest)
            # Verify the whole player, including licenses and runtime, after extraction.
            expected = game_hashes(folder, "NFC")
            archive = artifacts / (folder.name + ".zip")
            archive_tree(folder, archive)
            unpacked = Path(temp) / "roundtrip"
            unpacked.mkdir()
            extract_bundle(archive, unpacked)
            restored = unpacked / folder.name
            adapter.verify_roundtrip(restored)
            if game_hashes(restored, "NFC") != expected:
                raise ValueError("ZIP roundtrip changed packaged files")
            shutil.rmtree(folder)
            write_json(artifacts / adapter.MANIFEST, manifest)
            (artifacts / "SHA256SUMS.txt").write_text(
                "".join(
                    sha256(path) + "  " + path.name + "\n" for path in sorted(artifacts.iterdir())
                ),
                encoding="utf-8",
            )
            result = output / archive.name
        if source_revision(root, allow_dirty) != revision:
            raise ValueError("Source changed while the package was being built")
        artifacts.rename(output)
    print(result)
    return result
