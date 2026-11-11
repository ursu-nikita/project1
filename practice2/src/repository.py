"""NuGet HTTP metadata retrieval using only the standard library."""
import json
import re
import urllib.request
from xml.etree import ElementTree

TIMEOUT = 30
TARGET_FRAMEWORK = ".NETStandard2.0"


def download(url):
    """Fetch a resource with a timeout and an identifiable user agent."""
    request = urllib.request.Request(
        url, headers={"User-Agent": "Variant24DependencyGraph/1.0"}
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read()


def version_key(version):
    """Order numeric NuGet versions and their prerelease suffixes."""
    core, _, suffix = version.partition("-")
    numbers = tuple(int(x) for x in core.split("."))
    return numbers + (0,) * (4 - len(numbers)), not bool(suffix), suffix


def satisfies(version, requirement):
    """Match exact, minimum and bounded NuGet version ranges."""
    requirement = requirement.strip()
    key = version_key(version)
    if not requirement:
        return "-" not in version
    if requirement.startswith("[") and "," not in requirement:
        return key == version_key(requirement[1:-1])
    if requirement[0] not in "[(":
        return key >= version_key(requirement)
    lower, upper = requirement[1:-1].split(",", 1)
    lower_ok = not lower or (
        key >= version_key(lower.strip()) if requirement[0] == "["
        else key > version_key(lower.strip())
    )
    upper_ok = not upper or (
        key <= version_key(upper.strip()) if requirement[-1] == "]"
        else key < version_key(upper.strip())
    )
    return lower_ok and upper_ok


class NuGetRepository:
    """Retrieve package versions and parse .nuspec XML directly."""

    def __init__(self, url):
        index = json.loads(download(url))
        resources = index.get("resources", [])
        bases = [
            item["@id"] for item in resources
            if str(item.get("@type", "")).startswith("PackageBaseAddress")
        ]
        if not bases:
            raise ValueError("NuGet service has no PackageBaseAddress")
        self.base = bases[0].rstrip("/")
        self.cache = {}

    def resolve(self, package, requirement):
        """Choose the lowest stable version allowed by a range."""
        url = f"{self.base}/{package.lower()}/index.json"
        versions = json.loads(download(url))["versions"]
        matches = [v for v in versions if satisfies(v, requirement)]
        if not matches:
            raise ValueError(f"No version for {package} {requirement}")
        return min(matches, key=version_key)

    def dependencies(self, package, version):
        """Read dependencies for .NET Standard 2.0 from .nuspec."""
        key = (package.lower(), version.lower())
        if key not in self.cache:
            name, number = key
            url = f"{self.base}/{name}/{number}/{name}.nuspec"
            tree = ElementTree.fromstring(download(url))
            for node in tree.iter():
                node.tag = node.tag.split("}")[-1]
            self.cache[key] = self._extract(tree)
        return self.cache[key]

    def _extract(self, tree):
        """Select the closest supported .NET Standard dependency group."""
        parent = tree.find("./metadata/dependencies")
        if parent is None:
            return []
        groups = list(parent.findall("group"))
        if not groups:
            selected = parent
        else:
            eligible = []
            for group in groups:
                framework = group.get("targetFramework", "")
                match = re.fullmatch(
                    r"(?:\.NETStandard|netstandard)(\d+\.\d+)",
                    framework, re.IGNORECASE,
                )
                if match and float(match[1]) <= 2.0:
                    eligible.append((float(match[1]), group))
                elif not framework:
                    eligible.append((0.0, group))
            if not eligible:
                raise ValueError(
                    "No supported .NET Standard group in package"
                )
            selected = max(eligible, key=lambda item: item[0])[1]
        return [
            (node.attrib["id"], node.get("version", ""))
            for node in selected.findall("dependency")
        ]
