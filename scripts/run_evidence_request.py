#!/usr/bin/env python3
"""Send a request stored in a provider's evidence captures."""

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


MAX_INLINE_BODY_BYTES = 1_000_000


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
    parser.add_argument(
        "--save-response",
        action="store_true",
        help="save status, headers, final URL, and body beside the request",
    )
    return parser.parse_args()


def request_in_directory(directory: Path) -> Path:
    direct = directory / "request.json"
    if direct.is_file():
        return direct
    candidates = sorted(directory.glob("*.request.json"))
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise RepositoryError(f"{directory} does not contain a request file")
    raise RepositoryError(
        f"{directory} contains several request files; provide the exact file path"
    )


def stored_request_paths(server_dir: Path) -> list[Path]:
    return sorted((server_dir / "captures").rglob("*request.json"))


def load_request(request_arg: str, server_dir: Path) -> tuple[dict[str, Any], Path]:
    supplied = Path(request_arg)
    if supplied.is_file():
        path = supplied
    elif supplied.is_dir():
        path = request_in_directory(supplied)
    else:
        direct_matches = [
            path
            for path in stored_request_paths(server_dir)
            if path.parent.name == request_arg
        ]
        id_matches = []
        for candidate in stored_request_paths(server_dir):
            candidate_record = read_json(candidate)
            if (
                isinstance(candidate_record, dict)
                and candidate_record.get("id") == request_arg
            ):
                id_matches.append(candidate)
        matches = id_matches or direct_matches
        if len(matches) != 1:
            if not matches:
                raise RepositoryError(
                    f"no request named {request_arg!r} found below "
                    f"{server_dir / 'captures'}"
                )
            listed = ", ".join(str(path) for path in matches)
            raise RepositoryError(
                f"request name {request_arg!r} is ambiguous; use a path: {listed}"
            )
        path = matches[0]
    document = read_json(path)
    if not isinstance(document, dict):
        raise RepositoryError(f"{path} must contain a JSON object")
    return document, path


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
    saved_response_path: Path | None,
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
    response_headers = dict(response.headers.items())
    content_type = response.headers.get("Content-Type", "")
    charset = response.headers.get_content_charset() or "utf-8"
    response.close()

    if response_output is not None:
        response_output.parent.mkdir(parents=True, exist_ok=True)
        response_output.write_bytes(raw)

    if saved_response_path is not None:
        saved_response_path.parent.mkdir(parents=True, exist_ok=True)
        media_type = content_type.partition(";")[0].strip().lower()
        textual = (
            media_type.startswith("text/")
            or "json" in media_type
            or "xml" in media_type
            or media_type in {"application/javascript", "application/yaml"}
        )
        response_body: dict[str, Any]
        if not raw:
            response_body = {"body": ""}
        elif len(raw) <= MAX_INLINE_BODY_BYTES and textual:
            decoded = raw.decode(charset, errors="replace")
            try:
                saved_body: Any = json.loads(decoded)
            except json.JSONDecodeError:
                saved_body = decoded
            response_body = {"body": saved_body}
        else:
            extensions = {
                "application/geo+json": ".geojson",
                "application/json": ".json",
                "application/problem+json": ".json",
                "text/csv": ".csv",
                "text/html": ".html",
                "text/plain": ".txt",
                "text/xml": ".xml",
                "application/xml": ".xml",
                "image/tiff": ".tif",
            }
            prefix = saved_response_path.name.removesuffix(".response.json")
            prefix = "body" if prefix == "response.json" else f"{prefix}.body"
            body_path = saved_response_path.with_name(
                prefix + extensions.get(media_type, ".bin")
            )
            body_path.write_bytes(raw)
            response_body = {"body_file": body_path.name}
        saved_response = {
            "status": status,
            "headers": response_headers,
            "final_url": final_url,
            **response_body,
        }
        saved_response_path.write_text(
            json.dumps(saved_response, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Saved response: {saved_response_path}")

    print(f"Request: {record.get('id', '<unknown>')}")
    print(f"Method: {method}")
    print(f"URL: {final_url}")
    print(f"Status: {status}")
    print(f"Content-Type: {content_type}")
    print("Body:")
    print(raw.decode(charset, errors="replace"))

    expected = record.get("expected_status")
    if expected is None:
        return 0
    statuses = expected if isinstance(expected, list) else [expected]
    return 0 if status in statuses else 1


def paired_response_path(request_path: Path) -> Path:
    if request_path.name == "request.json":
        return request_path.with_name("response.json")
    return request_path.with_name(
        request_path.name.replace(".request.json", ".response.json")
    )


def main() -> int:
    args = parse_args()
    try:
        server, server_dir = load_server(args.server)
        record, request_path = load_request(args.request, server_dir)
        base_url = server_base_url(server, args.base_url)
        method, url, headers, body = prepare_request(record, base_url)
    except (OSError, RepositoryError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.print_curl:
        print_curl(method, url, headers, body)
        return 0
    saved_response_path = (
        paired_response_path(request_path) if args.save_response else None
    )
    return execute(
        record,
        method,
        url,
        headers,
        body,
        args.response_output,
        saved_response_path,
    )


if __name__ == "__main__":
    raise SystemExit(main())
