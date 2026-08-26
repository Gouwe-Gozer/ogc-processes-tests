#!/usr/bin/env python3
"""Capture process-description bodies plus status, headers, and final URLs."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from support.repository import (
    RepositoryError,
    load_server,
    server_base_url,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("process_ids", nargs="+", help="process IDs to capture")
    parser.add_argument(
        "--server", default="zoo-local", help="server evidence folder"
    )
    parser.add_argument("--base-url", help="override deployment base_url.default")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="override the server descriptions response directory",
    )
    parser.add_argument("--timeout", type=float, default=20.0)
    return parser.parse_args()


def safe_name(process_id: str) -> str:
    return urllib.parse.quote(process_id, safe="._-")


def capture_one(process_id: str, base_url: str, output_dir: Path, timeout: float) -> bool:
    encoded = urllib.parse.quote(process_id, safe="")
    url = f"{base_url}/processes/{encoded}"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        response = urllib.request.urlopen(request, timeout=timeout)
    except urllib.error.HTTPError as error:
        response = error
    except urllib.error.URLError as error:
        print(f"failed: {process_id}: {error}", file=sys.stderr)
        return False

    raw = response.read()
    status = response.status
    headers = dict(response.headers.items())
    final_url = response.geturl()
    content_type = response.headers.get_content_type()
    charset = response.headers.get_content_charset() or "utf-8"
    response.close()

    stem = f"{safe_name(process_id)}.process"
    parsed = None
    try:
        parsed = json.loads(raw.decode(charset))
    except (UnicodeDecodeError, json.JSONDecodeError):
        pass

    if parsed is not None:
        body_path = output_dir / f"{stem}.json"
        body_path.write_text(
            json.dumps(parsed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        metadata_path = output_dir / f"{stem}.metadata.json"
    else:
        extension = "html" if content_type == "text/html" else "txt"
        body_path = output_dir / f"{stem}-error.{extension}"
        body_path.write_bytes(raw)
        metadata_path = output_dir / f"{stem}-error.metadata.json"

    metadata = {
        "process_id": process_id,
        "request": {"method": "GET", "url": url, "headers": {"Accept": "application/json"}},
        "response": {
            "status": status,
            "headers": headers,
            "final_url": final_url,
            "body_file": body_path.name,
        },
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"captured: {process_id}: HTTP {status} -> {body_path}")
    return status < 400


def main() -> int:
    args = parse_args()
    try:
        server, server_dir = load_server(args.server)
        base_url = server_base_url(server, args.base_url)
        output_dir = args.output_dir or server_dir / "responses" / "descriptions"
        output_dir.mkdir(parents=True, exist_ok=True)
    except (OSError, RepositoryError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    successes = [
        capture_one(process_id, base_url, output_dir, args.timeout)
        for process_id in args.process_ids
    ]
    return 0 if all(successes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
