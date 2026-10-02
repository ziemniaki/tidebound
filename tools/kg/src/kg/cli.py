"""Codex-operated local knowledge graph: import, query, edit, search and export."""

import argparse
import json
import sys
from pathlib import Path

from surrealdb import RecordID

from . import database, server, snapshot, storage
from .errors import DesignError


def parser():
    cli = argparse.ArgumentParser(prog="kg", description=__doc__)
    cli.add_argument("--db", type=Path, default=Path(".build/kg/server"))
    commands = cli.add_subparsers(dest="command", required=True)
    setup = commands.add_parser(
        "setup", help="Install the pinned server and create local credentials"
    )
    setup.add_argument("--port", type=int, default=8000)
    commands.add_parser("serve", help="Run the local database until Ctrl-C")
    commands.add_parser(
        "connection", help="Show browser connection details, including the local password"
    )
    validate = commands.add_parser(
        "validate", help="Check a Git snapshot without opening a database"
    )
    validate.add_argument("directory", type=Path)
    ingest = commands.add_parser("import", help="Import a snapshot into the graph")
    ingest.add_argument("directory", type=Path)
    ingest.add_argument(
        "--replace", action="store_true", help="Replace graph contents, including deletions"
    )
    export = commands.add_parser(
        "export", help="Export one JSON file per entity and its outgoing links"
    )
    export.add_argument("directory", type=Path)
    show = commands.add_parser(
        "show", help="Read an entity and its incoming/outgoing relationships"
    )
    show.add_argument("id")
    search = commands.add_parser(
        "search", help="Full-text search of entity names, descriptions and data"
    )
    search.add_argument("text")
    search.add_argument("--limit", type=int, default=20)
    put = commands.add_parser(
        "put", help="Write one JSON entity, replacing its properties and outgoing links"
    )
    put.add_argument("file", type=Path)
    query = commands.add_parser(
        "query", help="Execute a SurrealQL file, including writes; Codex authors the query"
    )
    query.add_argument("file", type=Path)
    query.add_argument("--params", type=Path, help="JSON parameter values")
    return cli


def encode(value):
    if isinstance(value, RecordID):
        return str(value)
    raise TypeError(f"Not JSON: {type(value).__name__}")


def execute(args):
    if args.command == "setup":
        return server.setup(args.db, args.port)
    if args.command == "connection":
        return server.connection(args.db)
    if args.command == "serve":
        with server.running(args.db) as process:
            print(
                f"KG is running at {server.endpoint(server.settings(args.db))}. "
                "Use kg connection for browser settings. Ctrl-C stops the server.",
                flush=True,
            )
            try:
                code = process.wait()
                if code:
                    raise DesignError(
                        f"SurrealDB exited with status {code}; see {args.db / 'server.log'}"
                    )
            except KeyboardInterrupt:
                pass
        return {"stopped": True}
    if args.command == "validate":
        graph, nodes = snapshot.load(args.directory)
        return {"valid": True, "graph": graph["id"], "entities": len(nodes)}
    if args.command == "import":
        graph, nodes = snapshot.load(args.directory)
    if args.command == "export":
        root, db = args.directory.resolve(), args.db.resolve()
        if root == db or root in db.parents or db in root.parents:
            raise DesignError("Snapshot export must be outside the database directory")
    with database.connect(args.db) as db:
        if args.command == "import":
            db.ingest(graph, nodes, replace=args.replace)
            return {"imported": len(nodes), "graph": graph["id"]}
        if args.command == "export":
            graph, nodes = db.export()
            snapshot.write(args.directory, graph, nodes)
            return {"exported": len(nodes), "directory": str(args.directory)}
        if args.command == "show":
            return db.show(args.id)
        if args.command == "search":
            return db.search(args.text, args.limit)
        if args.command == "put":
            db.put(storage.load(args.file))
            return {"updated": str(args.file)}
        if args.command == "query":
            params = storage.load(args.params) if args.params else {}
            if not isinstance(params, dict):
                raise DesignError("Query parameters must be a JSON object")
            return db.query(args.file.read_text(encoding="utf-8"), params)


def main():
    args = parser().parse_args()
    try:
        print(
            json.dumps(execute(args), indent=2, ensure_ascii=False, default=encode, allow_nan=False)
        )
        return 0
    except Exception as error:  # noqa: BLE001 - CLI boundary reports SDK and transport failures.
        print(f"kg: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
