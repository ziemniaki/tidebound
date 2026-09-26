"""Locate complete Unicode font families without assuming a Linux filesystem."""

from pathlib import Path
import os


def resolve_fonts(
    linux=Path("/usr/share/fonts/truetype"),
    mac=Path("/System/Library/Fonts/Supplemental"),
    windows=None,
):
    windows = windows or Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"

    def family(candidates):
        for folder, filenames in candidates:
            paths = [folder / name for name in filenames]
            if all(path.is_file() for path in paths):
                return paths
        raise RuntimeError(
            "PDF fonts are missing. Install Liberation Serif and DejaVu Sans on Linux, "
            "or Times New Roman and Arial on macOS/Windows."
        )

    serif = [
        "LiberationSerif-Regular.ttf",
        "LiberationSerif-Bold.ttf",
        "LiberationSerif-Italic.ttf",
        "LiberationSerif-BoldItalic.ttf",
    ]
    body = family(
        [
            (linux / "liberation", serif),
            (linux / "liberation2", serif),
            (
                mac,
                [
                    "Times New Roman.ttf",
                    "Times New Roman Bold.ttf",
                    "Times New Roman Italic.ttf",
                    "Times New Roman Bold Italic.ttf",
                ],
            ),
            (windows, ["times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf"]),
        ]
    )
    head = family(
        [
            (linux / "dejavu", ["DejaVuSans.ttf", "DejaVuSans-Bold.ttf"]),
            (mac, ["Arial.ttf", "Arial Bold.ttf"]),
            (windows, ["arial.ttf", "arialbd.ttf"]),
        ]
    )
    return dict(
        zip(
            ("Body", "Body-Bold", "Body-Italic", "Body-BoldItalic", "Head", "Head-Bold"),
            body + head,
        )
    )
