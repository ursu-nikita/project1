"""Compare independently collected graphs with official NuGet restore."""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src"))
from settings import read_settings
from repository import NuGetRepository
from graph import build_graph
from order import loading_order


def describe(settings, target, order):
    """Describe observed native edges and explain differences."""
    records = []
    records += [f"## {settings.package} {settings.version}", "",
                "### Независимый DFS порядок", "",
                " → ".join(f"{a}/{b}" for a, b in order), "",
                "### Штатный граф NuGet из project.assets.json", ""]
    for node, data in target.items():
        edges = data.get("dependencies", {})
        records.append(f"- {node} → {edges or 'нет зависимостей'}")
    records += ["", "### Сопоставление", "",
                "NuGet объединяет ограничения версий и учитывает "
                "приоритет прямых зависимостей. Учебный DFS хранит "
                "узлы как пары имя и версия и выбирает минимальную "
                "версию отдельно для каждого ребра. Поэтому могут "
                "появиться две версии одного пакета. Также штатный "
                "restore добавляет NETStandard.Library для целевой "
                "платформы, а учебный граф начинается с пакета.", ""]
    return records

def compare(dotnet, temporary):
    """Restore three isolated projects and compare dependency edges."""
    records = ["# Сравнение с dotnet restore", ""]
    for example in ("newtonsoft", "serilog", "logging"):
        settings = read_settings(BASE / f"examples/{example}.ini")
        directory = temporary / example
        directory.mkdir(parents=True, exist_ok=True)
        project = directory / "Comparison.csproj"
        project.write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
            '<TargetFramework>netstandard2.0</TargetFramework>'
            '</PropertyGroup><ItemGroup>'
            f'<PackageReference Include="{settings.package}" '
            f'Version="{settings.version}" />'
            '</ItemGroup></Project>', encoding="utf-8",
        )
        subprocess.run(
            [dotnet, "restore", str(project), "--source",
             "https://api.nuget.org/v3/index.json", "--nologo"],
            check=True, capture_output=True, timeout=180,
        )
        assets = json.loads(
            (directory / "obj/project.assets.json").read_text()
        )
        target = next(iter(assets["targets"].values()))
        graph = build_graph(NuGetRepository(settings.repository), settings)
        order, _ = loading_order(graph)
        records.extend(describe(settings, target, order))
    (BASE / "COMPARISON.md").write_text(
        "\n".join(records), encoding="utf-8"
    )


if __name__ == "__main__":
    compare(sys.argv[1], Path(sys.argv[2]).resolve())

