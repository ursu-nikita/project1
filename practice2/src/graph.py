"""Iterative graph traversal and deterministic test repository."""
import json
import re
from dataclasses import dataclass, field


class TestRepository:
    """A JSON adjacency list with uppercase package identifiers."""

    def __init__(self, filename):
        with open(filename, encoding="utf-8-sig") as stream:
            self.data = json.load(stream)
        if not isinstance(self.data, dict):
            raise ValueError("Test repository must be an object")
        for name, edges in self.data.items():
            if not re.fullmatch("[A-Z]+", name):
                raise ValueError(f"Invalid test package: {name}")
            if not isinstance(edges, list):
                raise ValueError(f"Dependencies of {name} must be a list")
            if any(edge not in self.data for edge in edges):
                raise ValueError(f"Missing dependency of {name}")

    def resolve(self, package, requirement):
        """Test packages use version 1.0.0."""
        if package not in self.data:
            raise ValueError(f"Unknown test package: {package}")
        if requirement not in ("", "1.0.0", "[1.0.0]"):
            raise ValueError("Test repository supports version 1.0.0")
        return "1.0.0"

    def dependencies(self, package, version):
        """Return direct adjacency-list edges."""
        self.resolve(package, version)
        return [(name, "1.0.0") for name in self.data[package]]


@dataclass
class Graph:
    """Versioned nodes, edges and minimum observed node depths."""
    root: tuple
    edges: dict = field(default_factory=dict)
    depths: dict = field(default_factory=dict)


def build_graph(repo, settings):
    """Use an explicit DFS stack, revisiting shorter shared paths."""
    root = (settings.package, settings.version)
    graph = Graph(root)
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        previous = graph.depths.get(node)
        if previous is not None and previous <= depth:
            continue
        graph.depths[node] = depth
        graph.edges.setdefault(node, [])
        if depth >= settings.max_depth:
            continue
        children = []
        for name, requirement in repo.dependencies(*node):
            if settings.exclude and settings.exclude.lower() in name.lower():
                continue
            version = repo.resolve(name, requirement)
            child = (name, version)
            children.append(child)
            graph.edges.setdefault(child, [])
        graph.edges[node] = children
        stack.extend((child, depth + 1) for child in reversed(children))
    return graph
