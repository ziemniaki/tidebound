"""Stage native players once; archive only release candidates."""

from pathlib import Path
import json
import shutil
import tempfile

from tidebound_dev.paths import ROOT
from tidebound_dev.art.ownership import validate as validate_assets
from tidebound_dev.content.ownership import validate as validate_content
from tidebound_dev.runtime.config import SAVE_DIRECTORY, DEV_SAVES, PLAYTEST_SAVES, isolated_saves
from tidebound_dev.release.metadata import check_sources, source_revision
from tidebound_dev.release.artifacts import write_checksums
from tidebound_dev.maps.validate import validate
from . import linux, mac, windows
from .archives import archive_tree, copy_game, copy_verified, extract_bundle, game_hashes

PLATFORMS = {"mac": mac, "windows": windows, "linux": linux}


def development_settings(game, namespace=DEV_SAVES):
    path = game / "mkxp.json"
    text = isolated_saves(path.read_text(encoding="utf-8"), namespace)
    path.write_text(text, encoding="utf-8")


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def stage_player(
    folder,
    platform,
    root,
    config,
    development=False,
    preview=None,
    start=None,
):
    """All modes use the same runtime, payload and platform finalization."""
    adapter = PLATFORMS[platform]
    folder.mkdir()
    player = adapter.prepare(folder, root, config, development)
    copy_game(root / "game", player.game)
    copy_verified(root / "docs/credits.md", folder / "CREDITS.md")
    copy_verified(root / f"docs/players/{platform}.txt", folder / "README.txt")
    if development:
        development_settings(player.game, PLAYTEST_SAVES if start else DEV_SAVES)
        if preview:
            from tidebound_dev.art.preview import prepare

            prepare(player.game, preview)
        if start:
            from tidebound_dev.scenarios import prepare

            prepare(player.game, start)
    adapter.finalize(player)
    return player


def build(
    platform, output, root=ROOT, allow_dirty=False, development=False, preview=None, start=None
):
    """Publish a complete player or verified ZIP atomically; preserve existing output."""
    if (preview or start) and not development:
        raise ValueError("Starting states and asset previews are for development only")
    if preview and start:
        raise ValueError("Choose an asset preview or a starting state")
    namespace = PLAYTEST_SAVES if start else DEV_SAVES
    output = output.resolve()
    if output.exists():
        raise FileExistsError(
            "Choose a new output directory; existing builds are never overwritten"
        )
    config = check_sources(root)
    revision = source_revision(root, allow_dirty)
    validate(root)
    validate_assets(root)
    validate_content(root)
    adapter = PLATFORMS[platform]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".tidebound-package-", dir=output.parent) as temp:
        artifacts = Path(temp) / "artifacts"
        artifacts.mkdir()
        folder = artifacts / f"Tidebound_{adapter.NAME}_{config['version']}_{adapter.ARCHITECTURE}"
        player = stage_player(folder, platform, root, config, development, preview, start)
        if development:
            result = output / folder.name / player.launcher.relative_to(folder)
            write_json(
                folder / "DEVELOPMENT.json",
                {
                    "kind": "development",
                    "platform": platform,
                    "save_directory": namespace,
                    "start": start["id"] if start else None,
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
            write_checksums(artifacts)
            result = output / archive.name
        if source_revision(root, allow_dirty) != revision:
            raise ValueError("Source changed while the package was being built")
        artifacts.rename(output)
    if development:
        print(f"Development saves: {namespace}")
        if start:
            print(f"Starting at {start['id']}: {start['location']}")
    print(result)
    return result
