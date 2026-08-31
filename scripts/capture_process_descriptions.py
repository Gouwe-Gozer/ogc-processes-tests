#!/usr/bin/env python3
"""Capture complete process-description exchanges."""

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
    response_header_map,
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
    headers = response_header_map(response.headers)
    final_url = response.geturl()
    content_type = response.headers.get_content_type()
    charset = response.headers.get_content_charset() or "utf-8"
    response.close()

    capture_dir = output_dir / safe_name(process_id)
    capture_dir.mkdir(parents=True, exist_ok=True)
    request_record = {
        "method": "GET",
        "url": f"{{{{baseUrl}}}}/processes/{encoded}",
        "headers": {"Accept": "application/json"},
    }
    (capture_dir / "request.json").write_text(
        json.dumps(request_record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    for old_body in capture_dir.glob("body.*"):
        old_body.unlink()

    parsed = None
    try:
        parsed = json.loads(raw.decode(charset))
    except (UnicodeDecodeError, json.JSONDecodeError):
        pass

    if parsed is not None:
        response_body = {"body": parsed}
    else:
        extension = "html" if content_type == "text/html" else "txt"
        body_path = capture_dir / f"body.{extension}"
        body_path.write_bytes(raw)
        response_body = {"body_file": body_path.name}

    response_record = {
        "status": status,
        "headers": headers,
        "final_url": final_url,
        **response_body,
    }
    (capture_dir / "response.json").write_text(
        json.dumps(response_record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    legacy_body = capture_dir / "response-body.json"
    if legacy_body.exists():
        legacy_body.unlink()
    print(f"captured: {process_id}: HTTP {status} -> {capture_dir}")
    return status < 400


def main() -> int:
    args = parse_args()
    try:
        server, server_dir = load_server(args.server)
        base_url = server_base_url(server, args.base_url)
        output_dir = args.output_dir or server_dir / "captures" / "descriptions"
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
