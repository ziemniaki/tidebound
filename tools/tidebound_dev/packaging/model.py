"""The paths and provenance produced by a platform adapter."""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Player:
    folder: Path
    game: Path
    launcher: Path
    metadata: dict
