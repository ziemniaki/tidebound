"""Check Tidebound's exported graph and source relationships, not game execution."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from kg import database, snapshot

from tools.kg.tests.support import local_server

ROOT = Path(__file__).resolve().parents[2]


class TideboundKnowledge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph, values = snapshot.load(ROOT / "knowledge/tidebound")
        cls.nodes = {n["id"]: n for n in values}

    def test_source_links_target_sources_in_the_same_graph(self):
        for ident, node in self.nodes.items():
            if node["kind"] == "source":
                continue
            with self.subTest(id=ident):
                sources = [e["to"] for e in node["links"] if e["kind"] == "sourced_from"]
                self.assertTrue(all(self.nodes[s]["kind"] == "source" for s in sources))

    def test_distinct_people_survive_conversion(self):
        self.assertEqual(self.nodes["road_thief"]["name"], self.nodes["fisher_toma"]["name"])
        self.assertIn({"kind": "portrays", "to": "koga"}, self.nodes["false_koga"]["links"])

    def test_real_graph_can_search_and_follow_sources(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            local_server(Path(directory) / "world"),
            database.connect(Path(directory) / "world") as graph,
        ):
            graph.ingest(self.graph, list(self.nodes.values()))
            self.assertEqual(
                set(graph.query("SELECT VALUE <string>id FROM entity;")[0]),
                {f"entity:{ident}" for ident in self.nodes},
            )
            self.assertTrue(graph.search("necklace"))
            self.assertIn("species_whyduck", [n["id"].id for n in graph.search("hemispheres")])
            self.assertIn("maku", [n["id"].id for n in graph.search("turnips")])
            self.assertIn("lapras_apparition", [n["id"].id for n in graph.search("involuntary")])
            source_ids = graph.query("""
                    SELECT ->link[WHERE kind='sourced_from']->entity.id AS sources
                    FROM entity:necklace;
                """)[0][0]["sources"]
            self.assertTrue(source_ids)
            self.assertTrue(all(ident.id in self.nodes for ident in source_ids))
            exported_graph, exported_nodes = graph.export()
            expected = [
                {**n, "links": sorted(n["links"], key=lambda e: (e["kind"], e["to"]))}
                for n in sorted(self.nodes.values(), key=lambda n: n["id"])
            ]
            actual = [
                {**n, "links": sorted(n["links"], key=lambda e: (e["kind"], e["to"]))}
                for n in exported_nodes
            ]
            self.assertEqual(exported_graph, self.graph)
            self.assertEqual(actual, expected)

    def test_full_text_index_survives_a_bulk_import_process_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, "-m", "kg.cli", "--db", str(Path(directory) / "world")]
            with local_server(Path(directory) / "world"):
                imported = subprocess.run(
                    [*command, "import", str(ROOT / "knowledge/tidebound")],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(imported.returncode, 0, imported.stderr)
            with local_server(Path(directory) / "world"):
                searched = subprocess.run(
                    [*command, "search", "necklace"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(searched.returncode, 0, searched.stderr)
                self.assertIn("entity:necklace", [n["id"] for n in json.loads(searched.stdout)])


if __name__ == "__main__":
    unittest.main()
