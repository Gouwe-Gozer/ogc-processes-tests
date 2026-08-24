#!/usr/bin/env python3
"""Capture process descriptions as machine-readable interoperability evidence."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("process_ids", nargs="+", help="process IDs to capture")
    parser.add_argument("--base-url", required=True, help="OGC API base URL")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("evidence/zoo"),
        help="directory for <process_id>.process.json files",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for process_id in args.process_ids:
        encoded_id = urllib.parse.quote(process_id, safe="")
        url = f"{args.base_url.rstrip('/')}/processes/{encoded_id}"
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                document = json.load(response)
        except (urllib.error.URLError, json.JSONDecodeError) as error:
            print(f"failed: {process_id}: {error}")
            return 1

        output_path = args.output_dir / f"{process_id}.process.json"
        output_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"captured: {process_id} -> {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
