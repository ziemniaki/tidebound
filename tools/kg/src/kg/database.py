"""Shared local SurrealDB storage and native graph/full-text queries. No model calls."""

from contextlib import contextmanager

from surrealdb import RecordID, Surreal

from . import server, snapshot, storage
from .errors import DesignError

SEARCH_INDEXES = "\n".join(
    f"DEFINE INDEX IF NOT EXISTS entity_{field}_text ON entity "
    f"FIELDS {field} FULLTEXT ANALYZER words BM25;"
    for field in ("name", "description", "data")
)

SCHEMA = (
    """
DEFINE TABLE IF NOT EXISTS metadata SCHEMALESS;
DEFINE TABLE IF NOT EXISTS entity SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS kind ON entity TYPE string;
DEFINE FIELD IF NOT EXISTS name ON entity TYPE string;
DEFINE FIELD IF NOT EXISTS description ON entity TYPE string;
DEFINE FIELD OVERWRITE data ON entity TYPE option<object> FLEXIBLE
    VALUE IF $value = {} THEN NONE ELSE $value END;
DEFINE ANALYZER IF NOT EXISTS words TOKENIZERS blank, class FILTERS lowercase, ascii;
DEFINE TABLE IF NOT EXISTS link TYPE RELATION IN entity OUT entity ENFORCED SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS kind ON link TYPE string;
DEFINE FIELD IF NOT EXISTS description ON link TYPE option<string>;
DEFINE FIELD OVERWRITE data ON link TYPE option<object> FLEXIBLE
    VALUE IF $value = {} THEN NONE ELSE $value END;
DEFINE INDEX IF NOT EXISTS link_identity ON link FIELDS in, kind, out UNIQUE;
"""
    + SEARCH_INDEXES
    + f"""
DEFINE FIELD IF NOT EXISTS id ON entity ASSERT
    type::is_string(record::id($value))
    AND string::len(record::id($value)) <= 180
    AND string::matches(record::id($value), '{snapshot.ID_PATTERN}');
"""
)


@contextmanager
def connect(path):
    config = server.settings(path)
    with Surreal(server.endpoint(config)) as db:
        db.signin({"username": "kg", "password": config["password"]})
        graph = Graph(db)
        graph.query(
            "DEFINE NAMESPACE IF NOT EXISTS kg; USE NS kg; DEFINE DATABASE IF NOT EXISTS kg;"
        )
        db.use("kg", "kg")
        graph.query(SCHEMA)
        yield graph


class Graph:
    def __init__(self, db):
        self.db = db

    def query(self, sql, params=None):
        response = self.db.query_raw(sql, params or {})
        if "error" in response:
            raise DesignError(response["error"]["message"])
        results = response["result"]
        errors = [r["result"] for r in results if r["status"] != "OK"]
        if errors:
            raise DesignError("; ".join(map(str, errors)))
        return [r["result"] for r in results]

    def metadata(self):
        value = self.query("SELECT * OMIT id FROM ONLY metadata:graph;")[0]
        if value is None:
            raise DesignError("No graph yet. Import a snapshot first.")
        return {"format": value["format"], "id": value["graph_id"], "title": value["title"]}

    def ingest(self, graph, nodes, *, replace=False):
        snapshot.validate(graph, nodes)
        current = self.query("SELECT * FROM ONLY metadata:graph;")[0]
        if current and current["graph_id"] != graph["id"]:
            raise DesignError("Database belongs to a different graph; use another --db path")
        self._write(nodes, graph=graph, replace=replace)

    def put(self, value):
        self.metadata()
        snapshot.node(value)
        self._write([value])

    def _write(self, nodes, graph=None, replace=False):
        edges = [
            {
                "from": n["id"],
                "edge": storage.digest([n["id"], e["kind"], e["to"]]),
                **e,
            }
            for n in nodes
            for e in n["links"]
        ]
        # JSON literals preserve nulls independently of SDK parameter encoding.
        # Only serialized values enter the statement, never unquoted source text.
        sql = (
            "BEGIN TRANSACTION;\n"
            f"LET $nodes = {storage.canonical(nodes)};\n"
            f"LET $edges = {storage.canonical(edges)};\n"
        )
        if replace:
            sql += "DELETE link; DELETE entity;\n"
        if graph:
            sql += "UPSERT metadata:graph CONTENT $metadata;\n"
        sql += """
            FOR $node IN $nodes {
                LET $id = type::record('entity', $node.id);
                UPSERT $id CONTENT {
                    kind: $node.kind, name: $node.name,
                    description: $node.description, data: $node.data
                };
                DELETE link WHERE in = $id;
            };
            FOR $edge IN $edges {
                LET $origin = type::record('entity', $edge.from);
                LET $target = type::record('entity', $edge.to);
                LET $id = type::record('link', $edge.edge);
                IF !(record::exists($origin) AND record::exists($target)) {
                    THROW 'Missing relationship endpoint';
                };
                RELATE $origin->$id->$target CONTENT {
                    kind: $edge.kind, description: $edge.description, data: $edge.data
                };
            };
        """
        sql += "COMMIT TRANSACTION;"
        self.query(
            sql,
            {
                "metadata": (
                    {"format": graph["format"], "graph_id": graph["id"], "title": graph["title"]}
                    if graph
                    else {}
                ),
            },
        )

    def export(self):
        result = self.query("""
            RETURN {
                metadata: (SELECT * FROM ONLY metadata:graph),
                nodes: (SELECT * FROM entity),
                edges: (SELECT * FROM link)
            };
        """)[0]
        meta = result["metadata"]
        if meta is None:
            raise DesignError("No graph yet. Import a snapshot first.")
        graph = {"format": meta["format"], "id": meta["graph_id"], "title": meta["title"]}
        nodes = {}
        for raw in result["nodes"]:
            ident = raw["id"].id
            nodes[ident] = {**raw, "id": ident, "links": []}
        for edge in result["edges"]:
            nodes[edge["in"].id]["links"].append(
                {
                    "kind": edge["kind"],
                    "to": edge["out"].id,
                    **({"description": edge["description"]} if "description" in edge else {}),
                    **({"data": edge["data"]} if edge.get("data") else {}),
                }
            )
        values = sorted(nodes.values(), key=lambda n: n["id"])
        snapshot.validate(graph, values)
        return graph, values

    def show(self, ident):
        value = self.query("SELECT * FROM ONLY $id;", {"id": RecordID("entity", ident)})[0]
        if value is None:
            raise DesignError(f"Unknown entity: {ident}")
        outgoing = self.query("SELECT * FROM link WHERE in = $id;", {"id": value["id"]})[0]
        incoming = self.query("SELECT * FROM link WHERE out = $id;", {"id": value["id"]})[0]
        return {
            "node": {
                **value,
                "id": ident,
                "links": [
                    {
                        "kind": e["kind"],
                        "to": e["out"].id,
                        **({"description": e["description"]} if "description" in e else {}),
                        **({"data": e["data"]} if e.get("data") else {}),
                    }
                    for e in outgoing
                ],
            },
            "incoming": [
                {
                    "kind": e["kind"],
                    "from": e["in"].id,
                    **({"description": e["description"]} if "description" in e else {}),
                    **({"data": e["data"]} if e.get("data") else {}),
                }
                for e in incoming
            ],
        }

    def search(self, text, limit=20):
        if not text.strip() or not 1 <= limit <= 100:
            raise DesignError("Search needs text and a limit between 1 and 100")
        return self.query(
            """SELECT id, kind, name, description,
                      (search::score(1) ?? 0) * 3 + (search::score(2) ?? 0) * 2
                          + (search::score(3) ?? 0) AS score
               FROM entity
               WHERE name @1@ $text OR description @2@ $text OR data @3@ $text
               ORDER BY score DESC, id ASC LIMIT $limit;""",
            {"text": text, "limit": limit},
        )[0]
