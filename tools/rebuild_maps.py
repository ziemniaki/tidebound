"""Compile generated maps, tilesets and geometry after validation in isolation."""
from pathlib import Path
from tidebound_dev.maps.compiler import build

if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1])
