"""Inspect every native image and sign the assembled universal app on macOS."""
from pathlib import Path
import re
import subprocess
import sys

MACHO_MAGICS = {b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf", b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf"}


def run(*args):
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"{' '.join(args)} failed:\n{error.output}") from error


def native_images(app):
    images = []
    for path in sorted(app.rglob("*")):
        if path.is_file() and not path.is_symlink():
            with path.open("rb") as stream:
                if stream.read(4) in MACHO_MAGICS:
                    images.append(path)
    return images


def inspect_runtime(app, architectures):
    if sys.platform != "darwin":
        raise RuntimeError("Mac packaging requires macOS with Xcode command-line tools (lipo, otool, codesign)")
    images = native_images(app)
    if len(images) != 5:
        raise ValueError(f"Expected the five pinned runtime images, found {len(images)}")
    report = []
    for path in images:
        arches = run("lipo", "-archs", str(path)).split()
        if set(arches) != set(architectures):
            raise ValueError(f"Incomplete universal runtime: {path}: {arches}")
        for arch in architectures:
            commands = run("otool", "-arch", arch, "-l", str(path))
            minimum = re.search(r"cmd LC_BUILD_VERSION\n\s+cmdsize \d+\n\s+platform \d+\n\s+minos ([\d.]+)|"
                                r"cmd LC_VERSION_MIN_MACOSX\n\s+cmdsize \d+\n\s+version ([\d.]+)", commands)
            if not minimum:
                raise ValueError(f"Missing deployment target: {path} {arch}")
            version = next(group for group in minimum.groups() if group)
            limit = (10, 13) if arch == "x86_64" else (11, 0)
            if tuple(map(int, version.split(".")[:2])) > limit:
                raise ValueError(f"Deployment target regressed: {path} {arch} {version}")
            deps = []
            for line in run("otool", "-arch", arch, "-L", str(path)).splitlines():
                if not line.startswith("\t"):
                    continue
                dep = line.strip().split(" (", 1)[0]
                deps.append(dep)
                if dep.startswith(("/System/Library/", "/usr/lib/")):
                    continue
                bases = {"@rpath/": app / "Contents/Frameworks",
                         "@loader_path/": path.parent,
                         "@executable_path/": app / "Contents/MacOS"}
                resolved = next(((base / dep[len(prefix):]).resolve() for prefix, base in bases.items()
                                 if dep.startswith(prefix)), None)
                if resolved is None or not resolved.is_relative_to(app.resolve()) or not resolved.exists():
                    raise ValueError(f"Unbundled native dependency: {path}: {dep}")
            report.append({"file": path.relative_to(app).as_posix(), "arch": arch,
                           "minimum_macos": version, "dependencies": deps})
    return report


def sign_app(app):
    # Sign nested code before its containing bundle. No Developer ID identity or
    # notarization is implied by an ad-hoc integrity signature.
    for image in native_images(app):
        if "Frameworks" in image.parts:
            run("codesign", "--force", "--sign", "-", "--timestamp=none", str(image))
    for bundle in sorted(app.rglob("*.bundle"), key=lambda p: len(p.parts), reverse=True):
        run("codesign", "--force", "--sign", "-", "--timestamp=none", str(bundle))
    run("codesign", "--force", "--sign", "-", "--timestamp=none", str(app))
    run("codesign", "--verify", "--deep", "--strict", "--all-architectures", str(app))
