"""Compile all regional species, PBS and sprite exports in one pass."""
from pathlib import Path
from tidebound_dev.content.species_compiler import build

if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1])
