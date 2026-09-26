"""Checkout location shared by commands; callable operations also accept a root."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
