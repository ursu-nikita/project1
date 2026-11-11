"""Command-line entry point."""
import argparse
from settings import read_settings
from repository import NuGetRepository
from graph import TestRepository, build_graph
from order import loading_order
from visualize import render


def main():
    """Build a graph from the configured repository."""
    parser = argparse.ArgumentParser()
    parser.add_argument("config", nargs="?", default="config.ini")
    args = parser.parse_args()
    try:
        settings = read_settings(args.config)
        factory = TestRepository if settings.test_mode else NuGetRepository
        graph = build_graph(factory(settings.repository), settings)
        for node, children in graph.edges.items():
            print(f"{node}: {children}")
        order, cycles = loading_order(graph)
        print("Loading order:", " -> ".join(n[0] for n in order))
        if cycles:
            print("Cycle detected: no topological order exists", cycles)
        print("SVG:", render(graph, settings.output))
        return 0
    except Exception as error:
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


