#!/usr/bin/env python3
"""Copy repository fixtures into the local ZOO deployment's configured dataPath."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path, PurePosixPath

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from support.repository import (  # noqa: E402
    REPOSITORY_ROOT,
    RepositoryError,
    load_server,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--server", default="zoo-local", help="server evidence folder"
    )
    parser.add_argument("--container", help="override fixture_staging.container")
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=REPOSITORY_ROOT / "fixtures",
        help="local fixture directory",
    )
    parser.add_argument(
        "--destination", help="override fixture_staging.destination"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="show the resolved copy operation"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        server, _ = load_server(args.server)
        staging = server.get("fixture_staging")
        if not isinstance(staging, dict):
            raise RepositoryError(
                f"server {args.server!r} has no fixture_staging configuration"
            )
        container = args.container or staging.get("container")
        destination = args.destination or staging.get("destination")
        if not isinstance(container, str) or not container:
            raise RepositoryError("fixture_staging.container must be a string")
        if not isinstance(destination, str):
            raise RepositoryError("fixture_staging.destination must be a string")
    except RepositoryError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    fixtures_dir = args.fixtures_dir.resolve()
    destination_path = PurePosixPath(destination)
    allowed_root = PurePosixPath("/usr/com/zoo-project")
    if not fixtures_dir.is_dir():
        print(f"error: fixture directory does not exist: {fixtures_dir}", file=sys.stderr)
        return 2
    if not destination_path.is_absolute() or ".." in destination_path.parts:
        print("error: destination must be an absolute normalized path", file=sys.stderr)
        return 2
    if destination_path != allowed_root and allowed_root not in destination_path.parents:
        print(f"error: destination must stay below {allowed_root}", file=sys.stderr)
        return 2

    print(f"source: {fixtures_dir}")
    print(f"target: {container}:{destination}")
    if args.dry_run:
        return 0
    try:
        subprocess.run(
            ["docker", "exec", container, "mkdir", "-p", destination], check=True
        )
        subprocess.run(
            ["docker", "cp", f"{fixtures_dir}/.", f"{container}:{destination}"],
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"error: unable to stage fixtures: {error}", file=sys.stderr)
        return 1

    print("fixtures staged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
