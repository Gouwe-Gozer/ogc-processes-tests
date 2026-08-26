#!/usr/bin/env python3
"""Run one deployment probe and compare its HTTP status with the capture target."""

from __future__ import annotations

import argparse
import os
import shlex
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from support.repository import (
    RepositoryError,
    deployment_base_url,
    load_deployment,
    read_json,
    reference_path,
    resolve_url,
)


class PendingProbeError(ValueError):
    """Raised when a probe intentionally has no executable request yet."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("probe", help="probe ID or path to a probe directory")
    parser.add_argument(
        "--deployment", default="zoo-local", help="deployment manifest ID"
    )
    parser.add_argument("--base-url", help="override deployment base_url.default")
    parser.add_argument(
        "--print-curl", action="store_true", help="print curl without sending"
    )
    parser.add_argument(
        "--response-output", type=Path, help="write the raw response body here"
    )
    return parser.parse_args()


def load_probe(
    probe_arg: str, deployment_dir: Path, probes_name: str
) -> tuple[dict[str, Any], Path]:
    supplied = Path(probe_arg)
    probe_dir = (
        supplied if supplied.is_dir() else deployment_dir / probes_name / probe_arg
    )
    manifest_path = probe_dir / "probe.json"
    probe = read_json(manifest_path)
    if not isinstance(probe, dict):
        raise RepositoryError(f"{manifest_path} must contain a JSON object")
    if probe.get("status") == "pending":
        raise PendingProbeError(
            f"{probe.get('id', probe_dir.name)} is pending: {probe.get('notes', '')}"
        )
    if not isinstance(probe.get("request"), dict):
        raise RepositoryError(f"{manifest_path}: request must be an object")
    return probe, manifest_path


def prepare_request(
    probe: dict[str, Any], manifest_path: Path, base_url: str
) -> tuple[str, str, dict[str, str], Path | None, bytes | None]:
    request = probe["request"]
    method = request.get("method")
    target = request.get("path") or request.get("url")
    headers = request.get("headers", {})
    if method not in {"GET", "POST", "DELETE"}:
        raise RepositoryError("request.method must be GET, POST, or DELETE")
    if not isinstance(target, str):
        raise RepositoryError("request.path or request.url must be a string")
    if not isinstance(headers, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in headers.items()
    ):
        raise RepositoryError("request.headers must map strings to strings")

    body_path = None
    body = None
    body_file = request.get("body_file")
    if body_file is not None:
        if not isinstance(body_file, str):
            raise RepositoryError("request.body_file must be a string")
        body_path = reference_path(manifest_path, body_file)
        read_json(body_path)
        body = body_path.read_bytes()
    return method, resolve_url(target, base_url), headers, body_path, body


def print_curl(
    method: str, url: str, headers: dict[str, str], body_path: Path | None
) -> None:
    lines = [f"curl -X {method}", f"  {shlex.quote(url)}"]
    for key, value in headers.items():
        lines.append(f"  -H {shlex.quote(f'{key}: {value}')}")
    if body_path is not None:
        display = Path(os.path.relpath(body_path, Path.cwd()))
        lines.append(f"  --data @{shlex.quote(str(display))}")
    separator = " " + chr(92) + "\n"
    print(separator.join(lines))


def execute(
    probe: dict[str, Any],
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

    print(f"Probe: {probe.get('id', '<unknown>')}")
    print(f"Method: {method}")
    print(f"URL: {final_url}")
    print(f"Status: {status}")
    print(f"Content-Type: {content_type}")
    print("Body:")
    print(raw.decode(charset, errors="replace"))

    expected = probe.get("expected", {}).get("http_status")
    statuses = expected if isinstance(expected, list) else [expected]
    return 0 if status in statuses else 1


def main() -> int:
    args = parse_args()
    try:
        deployment, deployment_dir = load_deployment(args.deployment)
        probes_name = deployment.get("probes", "probes")
        if not isinstance(probes_name, str):
            raise RepositoryError("deployment probes must be a string")
        probe, manifest_path = load_probe(args.probe, deployment_dir, probes_name)
        base_url = deployment_base_url(deployment, args.base_url)
        method, url, headers, body_path, body = prepare_request(
            probe, manifest_path, base_url
        )
    except PendingProbeError as error:
        print(f"pending: {error}", file=sys.stderr)
        return 3
    except (OSError, RepositoryError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.print_curl:
        print_curl(method, url, headers, body_path)
        return 0
    return execute(probe, method, url, headers, body, args.response_output)


if __name__ == "__main__":
    raise SystemExit(main())
