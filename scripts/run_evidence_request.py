#!/usr/bin/env python3
"""Send one request stored below evidence/<server>/requests/."""

from __future__ import annotations

import argparse
import json
import shlex
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from support.repository import (
    RepositoryError,
    load_server,
    read_json,
    resolve_url,
    server_base_url,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", help="request ID, folder, or request.json path")
    parser.add_argument("--server", default="zoo-local", help="server evidence folder")
    parser.add_argument("--base-url", help="override server base_url.default")
    parser.add_argument(
        "--print-curl", action="store_true", help="print curl without sending"
    )
    parser.add_argument(
        "--response-output", type=Path, help="write the raw response body here"
    )
    return parser.parse_args()


def load_request(request_arg: str, server_dir: Path) -> dict[str, Any]:
    supplied = Path(request_arg)
    if supplied.is_file():
        path = supplied
    elif supplied.is_dir():
        path = supplied / "request.json"
    else:
        path = server_dir / "requests" / request_arg / "request.json"
    document = read_json(path)
    if not isinstance(document, dict):
        raise RepositoryError(f"{path} must contain a JSON object")
    return document


def prepare_request(
    record: dict[str, Any], base_url: str
) -> tuple[str, str, dict[str, str], bytes | None]:
    method = record.get("method")
    target = record.get("path") or record.get("url")
    headers = record.get("headers", {})
    if method not in {"GET", "POST", "DELETE"}:
        raise RepositoryError("method must be GET, POST, or DELETE")
    if not isinstance(target, str):
        raise RepositoryError("request must contain a string path or url")
    if not isinstance(headers, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in headers.items()
    ):
        raise RepositoryError("headers must map strings to strings")
    body = record.get("body")
    encoded_body = None
    if body is not None:
        encoded_body = json.dumps(body, ensure_ascii=False).encode("utf-8")
    return method, resolve_url(target, base_url), headers, encoded_body


def print_curl(
    method: str, url: str, headers: dict[str, str], body: bytes | None
) -> None:
    lines = [f"curl -X {method}", f"  {shlex.quote(url)}"]
    for key, value in headers.items():
        lines.append(f"  -H {shlex.quote(f'{key}: {value}')}")
    if body is not None:
        lines.append(f"  --data {shlex.quote(body.decode('utf-8'))}")
    separator = " " + chr(92) + "\n"
    print(separator.join(lines))


def execute(
    record: dict[str, Any],
    method: str,
    url: str,
    headers: dict[str, str],
    body: bytes | None,
    response_output: Path | None,
) -> int:
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        response = urllib.request.urlopen(request, timeout=60)
    except urllib.error.HTTPError as error:
        response = error
    except urllib.error.URLError as error:
        print(f"request failed: {error.reason}", file=sys.stderr)
        return 2

    raw = response.read()
    status = response.status
    final_url = response.geturl()
    content_type = response.headers.get("Content-Type", "")
    charset = response.headers.get_content_charset() or "utf-8"
    response.close()

    if response_output is not None:
        response_output.parent.mkdir(parents=True, exist_ok=True)
        response_output.write_bytes(raw)

    print(f"Request: {record.get('id', '<unknown>')}")
    print(f"Method: {method}")
    print(f"URL: {final_url}")
    print(f"Status: {status}")
    print(f"Content-Type: {content_type}")
    print("Body:")
    print(raw.decode(charset, errors="replace"))

    expected = record.get("expected_status")
    statuses = expected if isinstance(expected, list) else [expected]
    return 0 if status in statuses else 1


def main() -> int:
    args = parse_args()
    try:
        server, server_dir = load_server(args.server)
        record = load_request(args.request, server_dir)
        base_url = server_base_url(server, args.base_url)
        method, url, headers, body = prepare_request(record, base_url)
    except (OSError, RepositoryError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.print_curl:
        print_curl(method, url, headers, body)
        return 0
    return execute(record, method, url, headers, body, args.response_output)


if __name__ == "__main__":
    raise SystemExit(main())
