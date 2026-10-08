"""Small JSON snapshots of the graph for Git and structured ingestion."""

import math
import re
import shutil
import tempfile
from pathlib import Path

from . import storage
from .errors import DesignError

ID_PATTERN = r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$"


def identifier(value):
    if not isinstance(value, str) or len(value) > 180 or not re.fullmatch(ID_PATTERN, value):
        raise DesignError(
            f"Invalid stable ID: {value!r}; use lowercase snake_case (max 180 characters)"
        )


def fields(value, expected, optional=()):
    if (
        not isinstance(value, dict)
        or not set(expected) <= set(value)
        or set(value) - set(expected) - set(optional)
    ):
        raise DesignError(f"Expected fields: {', '.join(expected)}")


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise DesignError("Expected a nonempty string")


def json_value(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise DesignError("JSON object keys must be strings")
            json_value(item)
    elif isinstance(value, list):
        for item in value:
            json_value(item)
    elif type(value) is float and not math.isfinite(value):
        raise DesignError("Non-finite number")
    elif type(value) not in (str, int, float, bool, type(None)):
        raise DesignError(f"Not a JSON value: {type(value).__name__}")


def node(value):
    fields(value, ("id", "kind", "name", "description", "links"), optional=("data",))
    for key in ("id", "kind", "name"):
        text(value[key])
    identifier(value["id"])
    if not isinstance(value["description"], str) or not isinstance(value.get("data", {}), dict):
        raise DesignError("description must be text and data must be an object")
    json_value(value.get("data", {}))
    if not isinstance(value["links"], list):
        raise DesignError("links must be an array")
    found = set()
    for link in value["links"]:
        fields(link, ("kind", "to"), optional=("description", "data"))
        text(link["kind"])
        identifier(link["to"])
        if "description" in link:
            text(link["description"])
        if not isinstance(link.get("data", {}), dict):
            raise DesignError("Link data must be an object")
        json_value(link.get("data", {}))
        key = link["kind"], link["to"]
        if key in found:
            raise DesignError(f"Duplicate relationship on {value['id']}: {key}")
        found.add(key)


def validate(graph, nodes):
    fields(graph, ("format", "id", "title"))
    if graph["format"] != "kg/1":
        raise DesignError("Unsupported graph snapshot format")
    text(graph["id"])
    text(graph["title"])
    found = set()
    for value in nodes:
        node(value)
        if value["id"] in found:
            raise DesignError(f"Duplicate identity: {value['id']}")
        found.add(value["id"])
    for value in nodes:
        for link in value["links"]:
            if link["to"] not in found:
                raise DesignError(f"Missing relationship target: {value['id']} -> {link['to']}")


def load(root):
    root = Path(root)
    graph = storage.load(root / "graph.json")
    nodes = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise DesignError(f"Snapshot must not contain symlinks: {path}")
        if not path.is_file():
            continue
        if path == root / "graph.json":
            continue
        if path.suffix != ".json" or path.relative_to(root).parts[0] != "nodes":
            raise DesignError(f"Unexpected snapshot file: {path}")
        try:
            value = storage.load(path)
            node(value)
        except DesignError as error:
            raise DesignError(f"{path}: {error}") from None
        nodes.append(value)
    validate(graph, nodes)
    return graph, sorted(nodes, key=lambda n: n["id"])


def write(root, graph, nodes):
    """Replace only a recognized snapshot; preserve the old tree on write failure."""
    validate(graph, nodes)
    root = Path(root).absolute()
    if root.is_symlink():
        raise DesignError("Snapshot destination must not be a symlink")
    if root.exists():
        old, _ = load(root)
        if old["id"] != graph["id"]:
            raise DesignError("Destination belongs to a different graph")
    root.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".kg-export-", dir=root.parent) as temporary:
        staging = Path(temporary) / "new"
        backup = Path(temporary) / "old"
        storage.write(staging / "graph.json", graph)
        for value in nodes:
            value = {**value, "links": sorted(value["links"], key=lambda e: (e["kind"], e["to"]))}
            storage.write(staging / "nodes" / (value["id"] + ".json"), value)
        if root.exists():
            root.rename(backup)
        try:
            staging.rename(root)
        except OSError:
            if backup.exists():
                shutil.move(backup, root)
            raise
