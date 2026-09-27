"""Small, shared command surface for humans, agents and CI."""

from pathlib import Path
import argparse
import platform
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


def development_build(target, *, preview=None, start=None):
    if target == "mac" and sys.platform != "darwin":
        raise ValueError("Mac builds require macOS and Xcode command-line tools.")
    from .pipeline import rebuild

    from .art.preview import select

    asset = select(ROOT, preview) if preview else None
    from .scenarios import select as select_scenario

    rebuild(ROOT)
    state = select_scenario(ROOT, start) if start else None

    from .packaging.pipeline import build

    output = ROOT / ".build/dev" / (time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8])
    launcher = build(target, output, allow_dirty=True, development=True, preview=asset, start=state)
    print(f"\nReady: {launcher}", flush=True)
    return launcher


def parser():
    cli = argparse.ArgumentParser(prog="tidebound", description=__doc__)
    commands = cli.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Stage a development player")
    build_options = build.add_mutually_exclusive_group()
    build_options.add_argument(
        "--platform", choices=("mac", "windows", "linux"), help="Defaults to this computer"
    )
    build_options.add_argument(
        "--compile-only",
        action="store_true",
        help="Update the game and editor checkpoint without packaging a player",
    )
    play = commands.add_parser("play", help="Build and launch a development player")
    play.add_argument(
        "--from",
        dest="start",
        help="Start the full game at a declared state, e.g. neighbor/meal",
    )
    preview = commands.add_parser("preview", help="Build and launch the asset viewer")
    preview.add_argument("asset", help="Asset selector, e.g. pokemon/WHYDUCK or props/moored_ship")
    check = commands.add_parser("check", help="Verify the compiled game")
    check.add_argument("--all", action="store_true", help="Also verify isolated regeneration")
    package = commands.add_parser("package", help="Package one native player")
    package.add_argument("platform", choices=("mac", "windows", "linux"))
    package.add_argument("output", type=Path)
    package.add_argument("--allow-dirty", action="store_true")
    formatting = commands.add_parser("format", help="Format Python and Ruby")
    formatting.add_argument("--check", action="store_true")
    editor = commands.add_parser("editor", help="Import saved RPG Maker edits into source")
    editor.add_argument("action", choices=("import",))
    return cli


def execute(args):
    if args.command == "build" and args.compile_only:
        from .pipeline import rebuild

        rebuild(ROOT)
        print(f"Compiled project: {ROOT / 'game'}", flush=True)
        return
    if args.command in ("build", "play", "preview"):
        target = getattr(args, "platform", None) or host_platform()
        launcher = development_build(
            target, preview=getattr(args, "asset", None), start=getattr(args, "start", None)
        )
        if args.command != "build":
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
    elif args.command == "editor":
        from .maps.editor import import_changes

        import_changes(ROOT)
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


def preview():
    main(["preview", *sys.argv[1:]])


def check():
    main(["check", *sys.argv[1:]])


def editor():
    main(["editor", *sys.argv[1:]])


def format():
    main(["format", *sys.argv[1:]])
