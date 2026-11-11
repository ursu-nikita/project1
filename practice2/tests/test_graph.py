"""Regression tests for graph analysis and configuration."""
import dataclasses
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from graph import TestRepository, build_graph
from order import loading_order
from repository import satisfies
from settings import read_settings
from visualize import plantuml_text

BASE = Path(__file__).resolve().parents[1]


class GraphTests(unittest.TestCase):
    """Cover shared paths, cycles, filtering, depth and input errors."""

    def setUp(self):
        self.settings = read_settings(BASE / "examples/test.ini")

    def graph(self, **changes):
        settings = dataclasses.replace(self.settings, **changes)
        return build_graph(TestRepository(settings.repository), settings)

    def test_diamond(self):
        graph = self.graph()
        order, cycles = loading_order(graph)
        positions = {node: i for i, node in enumerate(order)}
        for node, children in graph.edges.items():
            for child in children:
                self.assertLess(positions[child], positions[node])
        self.assertFalse(cycles)
        self.assertEqual(len(order), 5)

    def test_cycles(self):
        graph = self.graph(repository=str(BASE / "examples/cycle.json"))
        order, cycles = loading_order(graph)
        self.assertEqual(len(order), 3)
        self.assertTrue(cycles)

    def test_depth_zero(self):
        self.assertEqual(len(self.graph(max_depth=0).edges), 1)

    def test_filter(self):
        graph = self.graph(exclude="B")
        self.assertNotIn(("B", "1.0.0"), graph.edges)

    def test_ranges(self):
        self.assertTrue(satisfies("2.0.0", "[1.0,3.0)"))
        self.assertFalse(satisfies("3.0.0", "[1.0,3.0)"))
        self.assertTrue(satisfies("1.0.0", "[1.0]"))

    def test_configuration_errors(self):
        original = (BASE / "examples/test.ini").read_text()
        original = original.replace("diamond.json",
                                    (BASE / "examples/diamond.json").as_posix())
        replacements = (
            ("package = A", "package = ?"),
            ("test_mode = true", "test_mode = maybe"),
            ("version = 1.0.0", "version = "),
            ("max_depth = 5", "max_depth = -1"),
            ("output = ../graphs/diamond.svg", "output = file.png"),
            ("repository = " + (BASE / "examples/diamond.json").as_posix(),
             "repository = absent.json"),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.ini"
            for old, new in replacements:
                with self.subTest(setting=old):
                    path.write_text(original.replace(old, new))
                    with self.assertRaises(ValueError):
                        read_settings(path)

    def test_plantuml(self):
        source = plantuml_text(self.graph())
        self.assertTrue(source.startswith("@startuml\n"))
        self.assertIn("-->", source)
        self.assertTrue(source.endswith("@enduml"))


if __name__ == "__main__":
    unittest.main()

