#!/usr/bin/env python3
"""Stage repository fixtures in the local ZOO Docker profile's dataPath."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--container",
        default="zoo-project-zoofpm-1",
        help="running ZOO container name",
    )
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=Path("fixtures"),
        help="local fixture directory",
    )
    parser.add_argument(
        "--destination",
        default="/usr/com/zoo-project/ogc-processes-tests/fixtures",
        help="fixture directory below the container's configured dataPath",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixtures_dir = args.fixtures_dir.resolve()
    if not fixtures_dir.is_dir():
        print(f"error: fixture directory does not exist: {fixtures_dir}")
        return 1
    if not args.destination.startswith("/usr/com/zoo-project/"):
        print("error: destination must stay below /usr/com/zoo-project/")
        return 1

    try:
        subprocess.run(
            ["docker", "exec", args.container, "mkdir", "-p", args.destination],
            check=True,
        )
        subprocess.run(
            ["docker", "cp", f"{fixtures_dir}/.", f"{args.container}:{args.destination}"],
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"error: unable to stage fixtures: {error}")
        return 1

    print(f"staged {fixtures_dir} in {args.container}:{args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
