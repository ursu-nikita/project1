"""Validated INI configuration for the NuGet graph tool."""
import configparser
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class Settings:
    """User-controlled analysis parameters."""
    package: str
    repository: str
    test_mode: bool
    version: str
    output: str
    max_depth: int
    exclude: str


def read_settings(filename):
    """Load all required values and report invalid configuration."""
    path = Path(filename).resolve()
    parser = configparser.ConfigParser(interpolation=None)
    if not parser.read(path, encoding="utf-8"):
        raise ValueError(f"Configuration not found: {path}")
    if "analysis" not in parser:
        raise ValueError("Missing [analysis] section")
    section = parser["analysis"]
    required = (
        "package", "repository", "test_mode", "version", "output",
        "max_depth", "exclude",
    )
    missing = set(required) - set(section)
    if missing:
        raise ValueError(f"Missing settings: {sorted(missing)}")
    settings = Settings(
        section["package"].strip(), section["repository"].strip(),
        section.getboolean("test_mode"), section["version"].strip(),
        section["output"].strip(), section.getint("max_depth"),
        section["exclude"].strip(),
    )
    validate(settings, path.parent)
    return settings


def validate(settings, base):
    """Validate names, paths, mode, version, depth and output format."""
    import re
    for name in ("package", "version"):
        value = getattr(settings, name)
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.+_-]*", value):
            raise ValueError(f"Invalid {name}: {value!r}")
    if settings.max_depth < 0:
        raise ValueError("max_depth must be nonnegative")
    if not settings.output or Path(settings.output).suffix != ".svg":
        raise ValueError("output must name an SVG file")
    settings.output = str((base / settings.output).resolve())
    if settings.test_mode:
        repository = (base / settings.repository).resolve()
        if not repository.is_file():
            raise ValueError(f"Repository not found: {repository}")
        settings.repository = str(repository)
    elif urlparse(settings.repository).scheme != "https":
        raise ValueError("repository must use HTTPS")
