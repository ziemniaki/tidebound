"""Canonical, strict JSON and atomic writes for portable artifacts."""

import hashlib
import json
import math
import os
import tempfile
from pathlib import Path

from .errors import DesignError


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def load(path):
    def pairs(entries):
        result = {}
        for key, value in entries:
            if key in result:
                raise DesignError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid(value):
        raise DesignError(f"Non-finite JSON number: {value}")

    def decimal(value):
        number = float(value)
        if not math.isfinite(number):
            invalid(value)
        return number

    try:
        return json.loads(
            Path(path).read_text(encoding="utf-8"),
            object_pairs_hook=pairs,
            parse_constant=invalid,
            parse_float=decimal,
        )
    except (json.JSONDecodeError, UnicodeError) as error:
        raise DesignError(f"{path}: {error}") from None


def write(path, value):
    path = Path(path)
    content = (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            name = stream.name
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)
