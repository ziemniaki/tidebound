"""Small, shared command surface for humans, agents and CI."""

from pathlib import Path
import argparse
import os
import platform
import shutil
import subprocess
import sys
import time
import uuid

from tidebound_dev.paths import ROOT


def run(*args, cwd=ROOT):
    print("+ " + " ".join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), cwd=cwd, check=True)


def host_platform():
    if sys.platform == "darwin":
        return "mac"
    if sys.platform == "win32":
        return "windows"
    if sys.platform.startswith("linux") and platform.machine().lower() in ("x86_64", "amd64"):
        return "linux"
    raise ValueError("Playable builds support macOS Intel/ARM, Windows x64 and Linux x86_64.")


def development_build(target, preview=None, scenario=None):
    if target == "mac" and sys.platform != "darwin":
        raise ValueError("Mac builds require macOS and Xcode command-line tools.")
    from .pipeline import rebuild

    from .art.preview import select

    asset = select(ROOT, preview) if preview else None
    from .scenarios import select as select_scenario

    state = select_scenario(ROOT, scenario) if scenario else None
    rebuild(ROOT)

    from .packaging.pipeline import build

    output = ROOT / ".build/dev" / (time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8])
    launcher = build(
        target, output, allow_dirty=True, development=True, preview=asset, scenario=state
    )
    print(f"\nReady: {launcher}", flush=True)
    return launcher


def open_editor():
    if sys.platform != "win32":
        raise ValueError(
            "RPG Maker XP requires Windows. Use uv run play for native Mac/Linux playtesting."
        )

    from tidebound_dev.release.metadata import load_release
    from tidebound_dev.files import sha256
    from tidebound_dev.runtime.inputs import windows_runtime, unpack_pinned

    config = load_release()
    sources = [windows_runtime(ROOT, config), unpack_pinned(ROOT, config, "windows_editor_archive")]
    for source in sources:
        for path in source.iterdir():
            dest = ROOT / "game" / path.name
            if dest.exists() and sha256(dest) != sha256(path):
                raise ValueError(
                    f"Preserving modified local file: {dest}. Move it aside before restoring the editor runtime."
                )
            shutil.copy2(path, dest)
    os.startfile(ROOT / "game/Game.rxproj")


def parser():
    cli = argparse.ArgumentParser(prog="tidebound", description=__doc__)
    commands = cli.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Stage a development player")
    build.add_argument(
        "--platform", choices=("mac", "windows", "linux"), help="Defaults to this computer"
    )
    play = commands.add_parser("play", help="Build and launch a development player")
    for command in (build, play):
        modes = command.add_mutually_exclusive_group()
        modes.add_argument(
            "--preview", help="Inspect an asset, e.g. pokemon/WHYDUCK or props/ship1"
        )
        modes.add_argument(
            "--scenario", help="Start a declared game state; list with uv run tidebound scenarios"
        )
    commands.add_parser("scenarios", help="List feature-owned playtest states")
    for name, help in (
        ("check", "Also verify isolated regeneration"),
        ("rebuild", "Also regenerate maps, content and artwork"),
    ):
        command = commands.add_parser(name)
        command.add_argument("--all", action="store_true", help=help)
    package = commands.add_parser("package", help="Package one native player")
    package.add_argument("platform", choices=("mac", "windows", "linux"))
    package.add_argument("output", type=Path)
    package.add_argument("--allow-dirty", action="store_true")
    formatting = commands.add_parser("format", help="Format Python and Ruby")
    formatting.add_argument("--check", action="store_true")
    commands.add_parser("editor", help="Restore and open the RPG Maker XP project")
    return cli


def execute(args):
    if args.command in ("build", "play"):
        target = getattr(args, "platform", None) or host_platform()
        launcher = development_build(target, args.preview, args.scenario)
        if args.command == "play":
            if target == "mac":
                run("open", "-n", "-W", launcher)
            else:
                run(launcher, cwd=launcher.parent)
    elif args.command == "package":
        from .packaging.pipeline import build

        build(args.platform, args.output, allow_dirty=args.allow_dirty)
    elif args.command == "check":
        from .checks import verify

        verify(ROOT, full=args.all)
    elif args.command == "rebuild":
        from .pipeline import rebuild

        rebuild(ROOT, full=args.all)
    elif args.command == "scenarios":
        from .scenarios import catalog, read

        for name, path in catalog(ROOT).items():
            print(f"{name}: {read(path)['description']}")
    elif args.command == "editor":
        open_editor()
    elif args.command == "format":
        from .formatting import format_sources

        format_sources(check=args.check)


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        execute(args)
    except (ValueError, OSError) as error:
        raise SystemExit(str(error)) from None
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from None


# uv aliases use the same parser and operations as `tidebound <command>`.


def build():
    main(["build", *sys.argv[1:]])


def play():
    main(["play", *sys.argv[1:]])


def check():
    main(["check", *sys.argv[1:]])


def rebuild():
    main(["rebuild", *sys.argv[1:]])


def editor():
    main(["editor", *sys.argv[1:]])


def format():
    main(["format", *sys.argv[1:]])
