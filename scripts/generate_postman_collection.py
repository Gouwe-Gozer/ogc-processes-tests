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


def create_execution_item(case_path: Path, case: dict[str, Any]) -> dict[str, Any]:
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


def create_process_description_item(
    process_id: str, case_names: list[str]
) -> dict[str, Any]:
    encoded_process_id = urllib.parse.quote(process_id, safe="")
    source_cases = ", ".join(f"cases/{name}" for name in case_names)
    return {
        "name": process_id,
        "request": {
            "method": "GET",
            "header": [{"key": "Accept", "value": "application/json"}],
            "url": f"{{{{baseUrl}}}}/processes/{encoded_process_id}",
            "description": (
                f"Process description used by the generated POST request(s).\n\n"
                f"Canonical case sources: {source_cases}"
            ),
        },
    }


def generate_collection(
    cases_dir: Path, base_url: str
) -> tuple[dict[str, Any], list[str], int, int]:
    execution_items = []
    process_cases: dict[str, list[str]] = {}
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
        execution_items.append(create_execution_item(case_path, case))
        process_id = case.get("process_id")
        if not isinstance(process_id, str):
            raise ValueError(f"{case_path}: process_id must be a string")
        process_cases.setdefault(process_id, []).append(case_path.parent.name)

    description_items = [
        create_process_description_item(process_id, process_cases[process_id])
        for process_id in sorted(process_cases, key=str.casefold)
    ]

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
        "item": [
            {
                "name": "POST_process_sync",
                "description": "Case-derived process execution requests.",
                "item": execution_items,
            },
            {
                "name": "process_descriptions",
                "description": (
                    "Process descriptions for every process represented in "
                    "POST_process_sync."
                ),
                "item": description_items,
            },
        ],
    }
    return collection, pending, len(execution_items), len(description_items)


def main() -> int:
    args = parse_args()
    try:
        collection, pending, execution_count, description_count = generate_collection(
            args.cases_dir, args.base_url
        )
    except (OSError, ValueError) as error:
        print(f"error: {error}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(collection, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"generated {execution_count} POST items and {description_count} "
        f"process descriptions in {args.output}"
    )
    if pending:
        print(f"skipped {len(pending)} pending cases: {', '.join(pending)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
