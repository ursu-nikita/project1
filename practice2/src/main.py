"""Command-line entry point."""
import argparse
from settings import read_settings
from repository import NuGetRepository


def main():
    """Print direct dependencies of the specified package version."""
    parser = argparse.ArgumentParser()
    parser.add_argument("config", nargs="?", default="config.ini")
    args = parser.parse_args()
    try:
        settings = read_settings(args.config)
        repo = NuGetRepository(settings.repository)
        for name, requirement in repo.dependencies(
            settings.package, settings.version
        ):
            print(f"{name} {requirement}")
        return 0
    except Exception as error:
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
