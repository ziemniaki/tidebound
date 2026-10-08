"""Exercise the real local server, persistence, transactions and Git roundtrips."""

import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from filelock import Timeout
from kg import database, server, snapshot, storage
from kg.errors import DesignError
from surrealdb.errors import SurrealError

from tools.kg.tests.support import local_server

GRAPH = {"format": "kg/1", "id": "test", "title": "Test graph"}


def node(ident, **changes):
    return {
        "id": ident,
        "kind": "character",
        "name": "Same name",
        "description": "",
        "links": [],
        **changes,
    }


def fixture():
    return [
        node(
            "hero",
            description="Carries the pearl necklace",
            data={"design": "A salt-stained coat"},
            links=[{"kind": "knows", "to": "other", "description": "Friends since the opening."}],
        ),
        node("other", description="Lives in the lighthouse"),
    ]


class LocalGraph(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "database"
        self.start_server()

    def start_server(self):
        self.running = local_server(self.path)
        self.running.__enter__()
        self.addCleanup(self.running.__exit__, None, None, None)

    def test_persistence_search_traversal_and_equal_names(self):
        with database.connect(self.path) as graph:
            graph.ingest(GRAPH, fixture())
        self.running.__exit__(None, None, None)
        self.start_server()
        with database.connect(self.path) as graph:
            self.assertEqual(graph.show("hero")["node"], fixture()[0])
            self.assertEqual(
                graph.show("other")["incoming"],
                [{"kind": "knows", "from": "hero", "description": "Friends since the opening."}],
            )
            self.assertEqual([row["id"].id for row in graph.search("pearl")], ["hero"])
            result = graph.query(
                "SELECT ->link[WHERE kind='knows']->entity.name AS names FROM entity:hero;"
            )
            self.assertEqual(result, [[{"names": ["Same name"]}]])
            graph.query("UPDATE link SET description='Met at the quay.';")
            self.assertEqual(
                graph.show("hero")["node"]["links"][0]["description"], "Met at the quay."
            )
            before = graph.export()
            for invalid in (None, {}, [], "", "  "):
                with self.subTest(description=invalid), self.assertRaises(DesignError):
                    graph.put(
                        node("hero", links=[{"kind": "knows", "to": "other", "description": invalid}])
                    )
                self.assertEqual(graph.export(), before)
            self.assertEqual(len(graph.export()[1]), 2)

    def test_put_rolls_back_everything_on_missing_endpoint(self):
        with database.connect(self.path) as graph:
            graph.ingest(GRAPH, fixture())
            before = graph.export()
            changed = node(
                "hero", name="Changed", links=[{"kind": "knows", "to": "missing", "data": {}}]
            )
            with self.assertRaisesRegex(DesignError, "endpoint"):
                graph.put(changed)
            self.assertEqual(graph.export(), before)

    def test_entity_ids_are_unquoted_and_invalid_writes_leave_graph_unchanged(self):
        with database.connect(self.path) as graph:
            values = [node(ident) for ident in ("winter_settlement", "species_arbok_1", "a" * 180)]
            graph.ingest(GRAPH, values)
            before = graph.export()
            rendered = graph.query("SELECT VALUE <string>id FROM entity;")[0]
            self.assertEqual(set(rendered), {f"entity:{n['id']}" for n in values})
            for ident in (
                "winter-settlement",
                "species/arbok_1",
                "Upper",
                "123",
                "a__b",
                "a_",
                "a" * 181,
            ):
                with self.subTest(id=ident):
                    with self.assertRaisesRegex(DesignError, "snake_case"):
                        graph.put(node(ident))
                    with self.assertRaises(DesignError):
                        graph.query(
                            "CREATE type::record('entity', $id) CONTENT "
                            "{kind: 'location', name: 'Invalid', description: '', data: {}};",
                            {"id": ident},
                        )
                    self.assertEqual(graph.export(), before)

    def test_structured_edit_replaces_outgoing_links_and_refreshes_search(self):
        with database.connect(self.path) as graph:
            graph.ingest(GRAPH, fixture())
            graph.put(node("hero", description="A sapphire compass"))
            self.assertEqual(graph.show("other")["incoming"], [])
            self.assertEqual(graph.search("pearl"), [])
            self.assertEqual(graph.search("sapphire")[0]["id"].id, "hero")
            graph.query("UPDATE entity:hero SET description=$text;", {"text": "An emerald lantern"})
            self.assertEqual(graph.search("sapphire"), [])
            self.assertEqual(graph.search("emerald")[0]["id"].id, "hero")

    def test_optional_data_stays_absent_across_writes_and_roundtrips(self):
        values = [
            node("hero", data={}, links=[{"kind": "knows", "to": "other", "data": {}}]),
            node("other"),
        ]
        expected = [node("hero", links=[{"kind": "knows", "to": "other"}]), node("other")]
        with database.connect(self.path) as graph:
            graph.ingest(GRAPH, values)
            self.assertNotIn("data", graph.query("SELECT * FROM ONLY entity:hero;")[0])
            self.assertNotIn("data", graph.query("SELECT * FROM link;")[0][0])
            self.assertNotIn("description", graph.query("SELECT * FROM link;")[0][0])
            self.assertEqual(graph.show("other")["incoming"], [{"kind": "knows", "from": "hero"}])
            self.assertEqual(graph.export(), (GRAPH, expected))
            folder = self.root / "optional-data"
            snapshot.write(folder, *graph.export())
            graph.ingest(*snapshot.load(folder), replace=True)
            self.assertEqual(graph.export(), (GRAPH, expected))
            nested = {"notes": {}, "answer": None, "design": "Verdigris"}
            graph.put(node("hero", data=nested))
            self.assertEqual(graph.show("hero")["node"]["data"], nested)
            self.assertEqual(graph.search("verdigris")[0]["id"].id, "hero")
            graph.query("UPDATE entity:hero SET data={};")
            self.assertNotIn("data", graph.show("hero")["node"])
            self.assertEqual(graph.search("verdigris"), [])
            for invalid in (None, [], "text"):
                with self.subTest(data=invalid), self.assertRaises(DesignError):
                    graph.put(node("hero", data=invalid))

    def test_search_indexes_nested_lore_and_dialogue_without_a_duplicate_field(self):
        with database.connect(self.path) as graph:
            graph.ingest(GRAPH, fixture())
            graph.put(
                node(
                    "hero",
                    data={
                        "visual": {"palette": "verdigris"},
                        "dialogue": [{"text": "Keep the latch loose."}],
                    },
                )
            )
            self.assertEqual(graph.search("verdigris")[0]["id"].id, "hero")
            self.assertEqual(graph.search("latch")[0]["id"].id, "hero")
            self.assertEqual(graph.search("palette"), [])
            self.assertNotIn("search", graph.query("SELECT * FROM ONLY entity:hero;")[0])
            graph.query("UPDATE entity:hero SET data.dialogue = [{text: 'Bring the ribbon.'}];")
            self.assertEqual(graph.search("latch"), [])
            self.assertEqual(graph.search("ribbon")[0]["id"].id, "hero")
            with self.assertRaises(DesignError):
                graph.query(
                    "BEGIN; UPDATE entity:hero SET data.visual.palette='amber'; THROW 'stop'; COMMIT;"
                )
            self.assertEqual(graph.search("amber"), [])
            self.assertEqual(graph.search("verdigris")[0]["id"].id, "hero")

    def test_native_transaction_failure_and_later_statement_errors_surface(self):
        with database.connect(self.path) as graph:
            graph.ingest(GRAPH, fixture())
            with self.assertRaisesRegex(DesignError, "failure"):
                graph.query("BEGIN; DELETE entity:hero; THROW 'failure'; COMMIT;")
            self.assertEqual(graph.show("hero")["node"], fixture()[0])
            with self.assertRaisesRegex(DesignError, "later error"):
                graph.query("RETURN 1; THROW 'later error';")

    def test_import_is_idempotent_and_replace_removes_deleted_nodes(self):
        with database.connect(self.path) as graph:
            graph.ingest(GRAPH, fixture())
            graph.ingest(GRAPH, fixture())
            self.assertEqual(len(graph.show("hero")["node"]["links"]), 1)
            graph.ingest(GRAPH, [node("new")])
            self.assertEqual(len(graph.export()[1]), 3)
            graph.ingest(GRAPH, [node("new")], replace=True)
            self.assertEqual(graph.export(), (GRAPH, [node("new")]))
            with self.assertRaisesRegex(DesignError, "different graph"):
                graph.ingest({**GRAPH, "id": "wrong"}, fixture(), replace=True)
            self.assertEqual(graph.export(), (GRAPH, [node("new")]))

    def test_export_import_keeps_nested_data_and_is_deterministic(self):
        values = fixture()
        values[0]["data"] = {
            "steps": ["second", "first"],
            "secret": {"revealed": False},
            "amount": None,
            "text": 'Line one\n"; DELETE entity; --\t\\ $name',
        }
        values[0]["links"][0]["description"] = 'After the return.\n"; DELETE link; --'
        values[0]["links"][0]["data"] = {"example": [None, {"value": 2}]}
        folder = self.root / "snapshot"
        with database.connect(self.path) as graph:
            graph.ingest(GRAPH, values)
            snapshot.write(folder, *graph.export())
        before = {p.relative_to(folder): p.read_bytes() for p in folder.rglob("*.json")}
        # The identity inside the record, not its filename, owns references.
        (folder / "nodes/hero.json").rename(folder / "nodes/renamed.json")
        with (
            local_server(self.root / "restored"),
            database.connect(self.root / "restored") as graph,
        ):
            graph.ingest(*snapshot.load(folder))
            self.assertEqual(graph.show("hero")["node"]["data"], values[0]["data"])
            self.assertEqual(graph.show("hero")["node"]["links"], values[0]["links"])
            snapshot.write(folder, *graph.export())
        after = {p.relative_to(folder): p.read_bytes() for p in folder.rglob("*.json")}
        self.assertEqual(before, after)
        snapshot.write(folder, GRAPH, [node("hero")])
        self.assertFalse((folder / "nodes/other.json").exists())

    def test_invalid_snapshots_do_not_overwrite_files(self):
        folder = self.root / "snapshot"
        snapshot.write(folder, GRAPH, fixture())
        before = (folder / "nodes/hero.json").read_bytes()
        invalid = deepcopy(fixture())
        invalid[0]["links"][0]["to"] = "missing"
        with self.assertRaisesRegex(DesignError, "Missing"):
            snapshot.write(folder, GRAPH, invalid)
        self.assertEqual((folder / "nodes/hero.json").read_bytes(), before)
        storage.write(folder / "nodes/duplicate.json", fixture()[0])
        with self.assertRaisesRegex(DesignError, "Duplicate"):
            snapshot.load(folder)
        unrelated = self.root / "unrelated"
        unrelated.mkdir()
        (unrelated / "keep.txt").write_text("keep me")
        with self.assertRaises(OSError):
            snapshot.write(unrelated, GRAPH, fixture())
        self.assertEqual((unrelated / "keep.txt").read_text(), "keep me")

    def test_cli_from_unrelated_directory_against_shared_server(self):
        folder = self.root / "input"
        snapshot.write(folder, GRAPH, fixture())

        def cli(*args, expected=0):
            result = subprocess.run(
                [sys.executable, "-m", "kg.cli", "--db", str(self.path), *map(str, args)],
                cwd=self.root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, expected, result.stderr)
            return json.loads(result.stdout) if result.returncode == 0 else result.stderr

        cli("validate", folder)
        cli("import", folder)
        self.assertEqual(cli("show", "hero")["node"]["id"], "hero")
        self.assertEqual(len(cli("search", "pearl")), 1)
        query = self.root / "query.surql"
        query.write_text("SELECT name FROM entity WHERE kind = $kind;")
        storage.write(self.root / "params.json", {"kind": "character"})
        self.assertEqual(len(cli("query", query, "--params", self.root / "params.json")[0]), 2)
        storage.write(self.root / "hero.json", node("hero", description="An opal"))
        cli("put", self.root / "hero.json")
        cli("export", self.root / "export")
        cli("export", self.path, expected=1)
        cli("show", "missing", expected=1)
        self.assertEqual(len(snapshot.load(self.root / "export")[1]), 2)

    def test_studio_client_and_cli_share_live_edits_and_authentication(self):
        from surrealdb import RecordID, Surreal

        with database.connect(self.path) as graph:
            graph.ingest(GRAPH, fixture())
            config = server.connection(self.path)
            with Surreal(config["endpoint"]) as studio:
                with self.assertRaises(SurrealError):
                    studio.signin({"username": "kg", "password": "wrong"})
                studio.signin({"username": "kg", "password": config["password"]})
                studio.use("kg", "kg")
                studio.query("UPDATE entity:hero SET description='A garnet pendant';")
                self.assertEqual(graph.search("garnet")[0]["id"].id, "hero")
                graph.put(node("hero", description="A ruby"))
                self.assertEqual(
                    studio.select(RecordID("entity", "hero"))[0]["description"], "A ruby"
                )
                studio.query("UPDATE entity:hero SET data.optional=NULL;")
                self.assertIsNone(graph.show("hero")["node"]["data"]["optional"])

    def test_conflicting_server_and_missing_configuration_fail_clearly(self):
        with self.assertRaises(Timeout), server.running(self.path):
            self.fail("A second server must not start")
        with (
            self.assertRaisesRegex(DesignError, "kg setup"),
            database.connect(self.root / "absent"),
        ):
            self.fail("Missing configuration must not create a second database")
        with (
            database.connect(self.path) as graph,
            self.assertRaisesRegex(DesignError, "Parse error"),
        ):
            graph.query("NOT VALID SURREALQL;")


if __name__ == "__main__":
    unittest.main()
