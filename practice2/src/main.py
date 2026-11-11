"""Command-line entry point."""
import argparse
from dataclasses import asdict
from settings import read_settings


def main():
    """Display validated configuration."""
    parser = argparse.ArgumentParser()
    parser.add_argument("config", nargs="?", default="config.ini")
    args = parser.parse_args()
    try:
        settings = read_settings(args.config)
        for key, value in asdict(settings).items():
            print(f"{key}={value}")
        return 0
    except (ValueError, OSError) as error:
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
