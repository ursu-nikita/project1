"""PlantUML source generation and local SVG rendering."""
from pathlib import Path
import os
import subprocess


def plantuml_text(graph):
    """Assign stable aliases and escape node labels."""
    nodes = sorted(graph.edges)
    aliases = {node: f"n{i}" for i, node in enumerate(nodes)}
    lines = ["@startuml", "!pragma layout smetana",
             "left to right direction", "skinparam shadowing false"]
    for node in nodes:
        label = f"{node[0]}\\n{node[1]}"
        label = label.replace('"', "'")
        lines.append(f'rectangle "{label}" as {aliases[node]}')
    for parent in nodes:
        for child in graph.edges[parent]:
            lines.append(f"{aliases[parent]} --> {aliases[child]}")
    lines.append("@enduml")
    return "\n".join(lines)


def render(graph, output):
    """Render through the official PlantUML JAR without a web service."""
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    source = destination.with_suffix(".puml")
    source.write_text(plantuml_text(graph), encoding="utf-8")
    default = Path(__file__).resolve().parents[1] / "tools/plantuml.jar"
    jar = Path(os.environ.get("PLANTUML_JAR", str(default)))
    if not jar.is_file():
        raise ValueError(
            "PlantUML missing: run setup.bat or set PLANTUML_JAR"
        )
    subprocess.run(
        ["java", "-jar", str(jar), "-tsvg", str(source.resolve())],
        check=True, capture_output=True, timeout=120,
    )
    if not destination.is_file():
        raise ValueError("PlantUML did not produce SVG")
    return destination

