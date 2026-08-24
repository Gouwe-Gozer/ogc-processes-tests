#!/usr/bin/env python3
"""Generate a Postman collection from canonical case directories."""

from __future__ import annotations

import argparse
import json
import urllib.parse
import uuid
from pathlib import Path
from typing import Any


COLLECTION_SCHEMA = (
    "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
)
COLLECTION_ID = str(
    uuid.uuid5(
        uuid.NAMESPACE_URL,
        "https://github.com/Gouwe-Gozer/ogc-processes-tests#postman-collection",
    )
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases-dir",
        type=Path,
        default=Path("cases"),
        help="directory containing one subdirectory per case",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("postman/ogc-processes-tests.postman_collection.json"),
        help="generated Postman collection path",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost/ogc-api",
        help="default value for the Postman baseUrl collection variable",
    )
    return parser.parse_args()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON from {path}: {error}") from error


def create_item(case_path: Path, case: dict[str, Any]) -> dict[str, Any]:
    case_name = case_path.parent.name
    try:
        process_id = case["process_id"]
        request_name = case["request"]
    except KeyError as error:
        raise ValueError(f"{case_path} is missing {error.args[0]}") from error

    if not isinstance(process_id, str) or not isinstance(request_name, str):
        raise ValueError(f"{case_path}: process_id and request must be strings")

    request_path = case_path.parent / request_name
    request_body = request_path.read_text(encoding="utf-8")
    read_json(request_path)

    headers = [{"key": "Content-Type", "value": "application/json"}]
    if case.get("execution_mode") == "async":
        headers.append({"key": "Prefer", "value": "respond-async"})

    description_parts = [str(case.get("title", case_name))]
    if case.get("notes"):
        description_parts.append(str(case["notes"]))
    description_parts.append(f"Canonical source: cases/{case_name}")

    encoded_process_id = urllib.parse.quote(process_id, safe="")
    return {
        "name": case_name,
        "request": {
            "method": "POST",
            "header": headers,
            "body": {
                "mode": "raw",
                "raw": request_body,
                "options": {"raw": {"language": "json"}},
            },
            "url": f"{{{{baseUrl}}}}/processes/{encoded_process_id}/execution",
            "description": "\n\n".join(description_parts),
        },
    }


def generate_collection(cases_dir: Path, base_url: str) -> tuple[dict[str, Any], list[str]]:
    items = []
    pending = []
    case_paths = sorted(cases_dir.glob("*/case.json"), key=lambda path: path.parent.name)
    if not case_paths:
        raise ValueError(f"no case.json files found below {cases_dir}")

    for case_path in case_paths:
        case = read_json(case_path)
        if not isinstance(case, dict):
            raise ValueError(f"{case_path} must contain a JSON object")
        if case.get("status") == "pending":
            pending.append(case_path.parent.name)
            continue
        items.append(create_item(case_path, case))

    collection = {
        "info": {
            "_postman_id": COLLECTION_ID,
            "name": "OGC API Processes tests",
            "description": (
                "Generated from the repository's canonical case.json and "
                "request.json files. Do not edit this collection by hand."
            ),
            "schema": COLLECTION_SCHEMA,
        },
        "variable": [
            {"key": "baseUrl", "value": base_url.rstrip("/"), "type": "string"}
        ],
        "item": items,
    }
    return collection, pending


def main() -> int:
    args = parse_args()
    try:
        collection, pending = generate_collection(args.cases_dir, args.base_url)
    except (OSError, ValueError) as error:
        print(f"error: {error}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(collection, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"generated {len(collection['item'])} items in {args.output}")
    if pending:
        print(f"skipped {len(pending)} pending cases: {', '.join(pending)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
