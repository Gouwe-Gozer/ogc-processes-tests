#!/usr/bin/env python3
"""Run one small OGC API Processes test case."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


class PendingCaseError(ValueError):
    """Raised when a case intentionally has no executable request yet."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute a canonical OGC API Processes case."
    )
    parser.add_argument("case_dir", type=Path, help="directory containing case.json")
    parser.add_argument(
        "--base-url",
        required=True,
        help="OGC API base URL, for example http://localhost/ogc-api",
    )
    parser.add_argument(
        "--print-curl",
        action="store_true",
        help="print an equivalent curl command without sending the request",
    )
    parser.add_argument(
        "--response-output",
        type=Path,
        help="write the raw response body to this evidence file",
    )
    return parser.parse_args()


def read_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON from {path}: {error}") from error


def load_case(case_dir: Path) -> tuple[dict[str, Any], Path | None, bytes | None]:
    case_path = case_dir / "case.json"
    case = read_json(case_path)
    if not isinstance(case, dict):
        raise ValueError(f"{case_path} must contain a JSON object")
    if case.get("status") == "pending":
        raise PendingCaseError(
            f"{case.get('id', case_dir.name)} is pending: {case.get('notes', '')}"
        )

    try:
        process_id = case["process_id"]
        expected_status = case["expected"]["http_status"]
    except (KeyError, TypeError) as error:
        raise ValueError(f"{case_path} is missing a required case field") from error

    if not isinstance(process_id, str):
        raise ValueError("process_id must be a string")
    if not isinstance(expected_status, int):
        raise ValueError("expected.http_status must be an integer")

    operation = case.get("operation", "execution")
    if operation == "process_description":
        return case, None, None
    if operation != "execution":
        raise ValueError("operation must be execution or process_description")

    try:
        request_name = case["request"]
    except KeyError as error:
        raise ValueError(f"{case_path} is missing a required case field") from error
    if not isinstance(request_name, str):
        raise ValueError("request must be a string")
    if case.get("execution_mode", "sync") not in {"sync", "async"}:
        raise ValueError("execution_mode must be sync or async")

    request_path = case_dir / request_name
    read_json(request_path)
    try:
        request_body = request_path.read_bytes()
    except OSError as error:
        raise ValueError(f"cannot read request body from {request_path}: {error}") from error
    return case, request_path, request_body


def case_url(base_url: str, process_id: str, operation: str) -> str:
    quoted_id = urllib.parse.quote(process_id, safe="")
    process_url = f"{base_url.rstrip('/')}/processes/{quoted_id}"
    if operation == "process_description":
        return process_url
    return f"{process_url}/execution"


def print_curl(
    url: str,
    request_path: Path | None,
    execution_mode: str,
    operation: str,
) -> None:
    if operation == "process_description":
        print("curl \\")
        print(f"  {shlex.quote(url)} \\")
        print("  -H 'Accept: application/json'")
        return

    if request_path is None:
        raise ValueError("execution case has no request path")
    display_path = Path(os.path.relpath(request_path, Path.cwd()))
    print("curl \\")
    print("  -X POST \\")
    print(f"  {shlex.quote(url)} \\")
    print("  -H 'Content-Type: application/json' \\")
    if execution_mode == "async":
        print("  -H 'Prefer: respond-async' \\")
    print(f"  --data @{shlex.quote(str(display_path))}")


def execute(
    case: dict[str, Any],
    url: str,
    body: bytes | None,
    response_output: Path | None = None,
) -> int:
    operation = case.get("operation", "execution")
    method = "GET" if operation == "process_description" else "POST"
    headers = (
        {"Accept": "application/json"}
        if operation == "process_description"
        else {"Content-Type": "application/json"}
    )
    if operation == "execution" and case.get("execution_mode") == "async":
        headers["Prefer"] = "respond-async"
    request = urllib.request.Request(
        url,
        data=body,
        headers=headers,
        method=method,
    )

    response = None
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as error:
        response = error
    except urllib.error.URLError as error:
        print(f"request failed: {error.reason}", file=sys.stderr)
        return 2

    status = response.status
    content_type = response.headers.get("Content-Type", "")
    charset = response.headers.get_content_charset() or "utf-8"
    raw_body = response.read().decode(charset, errors="replace")
    response.close()

    if response_output is not None:
        response_output.parent.mkdir(parents=True, exist_ok=True)
        response_output.write_text(raw_body.rstrip() + "\n", encoding="utf-8")

    print(f"Case: {case.get('id', '<unknown>')}")
    print(f"Method: {method}")
    print(f"URL: {url}")
    print(f"Status: {status}")
    print(f"Content-Type: {content_type}")
    print("Body:")
    print(raw_body)

    return 0 if status == case["expected"]["http_status"] else 1


def main() -> int:
    args = parse_args()
    try:
        case, request_path, body = load_case(args.case_dir)
    except PendingCaseError as error:
        print(f"pending: {error}", file=sys.stderr)
        return 3
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    operation = case.get("operation", "execution")
    url = case_url(args.base_url, case["process_id"], operation)
    if args.print_curl:
        print_curl(
            url,
            request_path,
            case.get("execution_mode", "sync"),
            operation,
        )
        return 0
    return execute(case, url, body, args.response_output)


if __name__ == "__main__":
    raise SystemExit(main())
