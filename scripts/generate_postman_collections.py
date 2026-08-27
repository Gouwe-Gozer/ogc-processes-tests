#!/usr/bin/env python3
"""Generate Postman collections from scenarios and runnable evidence requests."""

from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path
from typing import Any

from support.repository import REPOSITORY_ROOT, RepositoryError, read_json


COLLECTION_SCHEMA = (
    "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPOSITORY_ROOT / "generated" / "postman",
    )
    return parser.parse_args()


def collection_id(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"ogc-processes-tests:{name}"))


def headers(values: object) -> list[dict[str, str]]:
    if not isinstance(values, dict):
        return []
    return [{"key": str(key), "value": str(value)} for key, value in values.items()]


def raw_body(value: object) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, indent=2, ensure_ascii=False)


def postman_request(record: dict[str, Any], url: str) -> dict[str, Any]:
    request: dict[str, Any] = {
        "method": record["method"],
        "header": headers(record.get("headers")),
        "url": url,
    }
    if "body" in record:
        request["body"] = {
            "mode": "raw",
            "raw": raw_body(record["body"]),
            "options": {"raw": {"language": "json"}},
        }
    return request


def response_example(
    record: dict[str, Any],
    original_request: dict[str, Any],
    label: str | None = None,
) -> dict[str, Any]:
    name = f"HTTP {record['status']}"
    if label:
        name = f"{label.replace('-', ' ')} — {name}"
    return {
        "name": name,
        "originalRequest": original_request,
        "status": str(record["status"]),
        "code": record["status"],
        "header": headers(record.get("headers")),
        "body": raw_body(record.get("body", "")),
    }


def paired_responses(request_path: Path) -> list[tuple[str | None, Path]]:
    if request_path.name == "request.json":
        response_path = request_path.with_name("response.json")
        return [(None, response_path)] if response_path.is_file() else []

    prefix = request_path.name.removesuffix(".request.json")
    responses: list[tuple[str | None, Path]] = []
    response_path = request_path.with_name(f"{prefix}.response.json")
    if response_path.is_file():
        responses.append((None, response_path))
    for variant_path in sorted(request_path.parent.glob(f"{prefix}.*.response.json")):
        label = variant_path.name.removeprefix(f"{prefix}.").removesuffix(
            ".response.json"
        )
        responses.append((label, variant_path))
    return responses


def post_response_event(request_path: Path) -> list[dict[str, Any]]:
    if request_path.name == "request.json":
        script_path = request_path.with_name("post-response.js")
    else:
        script_path = request_path.with_name(
            request_path.name.replace(".request.json", ".post-response.js")
        )
    if not script_path.is_file():
        return []
    script = script_path.read_text(encoding="utf-8")
    return [
        {
            "listen": "test",
            "script": {
                "type": "text/javascript",
                "exec": script.rstrip().splitlines(),
            },
        }
    ]


def scenario_item(request_path: Path) -> dict[str, Any]:
    record = read_json(request_path)
    if not isinstance(record, dict):
        raise RepositoryError(f"{request_path} must contain an object")
    request = postman_request(record, str(record.get("url") or record.get("path")))
    name = request_path.name.removesuffix(".request.json")
    if name == "request.json":
        name = request_path.parent.name
    item: dict[str, Any] = {"name": name, "request": request}
    response_examples = []
    for label, response_path in paired_responses(request_path):
        response = read_json(response_path)
        if isinstance(response, dict):
            response_examples.append(response_example(response, request, label))
    if response_examples:
        item["response"] = response_examples
    events = post_response_event(request_path)
    if events:
        item["event"] = events
    return item


def add_to_tree(tree: dict[str, Any], parts: tuple[str, ...], item: dict[str, Any]) -> None:
    current = tree
    for part in parts:
        current = current.setdefault(part, {})
    current.setdefault("__items__", []).append(item)


def tree_items(tree: dict[str, Any]) -> list[dict[str, Any]]:
    result = list(tree.get("__items__", []))
    for name in sorted(key for key in tree if key != "__items__"):
        result.append({"name": name, "item": tree_items(tree[name])})
    return result


def generate_scenarios() -> dict[str, Any]:
    root = REPOSITORY_ROOT / "scenarios"
    request_paths = sorted(
        set(root.rglob("*.request.json")) | set(root.rglob("request.json"))
    )
    tree: dict[str, Any] = {}
    for path in request_paths:
        relative = path.parent.relative_to(root)
        add_to_tree(tree, relative.parts, scenario_item(path))
    return {
        "info": {
            "_postman_id": collection_id("representative-scenarios"),
            "name": "OGC API Processes representative scenarios",
            "description": "Generated from scenarios/. Do not edit by hand.",
            "schema": COLLECTION_SCHEMA,
        },
        "variable": [
            {"key": "baseUrl", "value": "http://localhost/ogc-api", "type": "string"},
            {"key": "jobId", "value": "", "type": "string"},
            {"key": "jobUrl", "value": "", "type": "string"},
            {"key": "resultsUrl", "value": "", "type": "string"},
            {"key": "jobStatus", "value": "", "type": "string"},
            {"key": "pollAttempt", "value": "0", "type": "string"},
            {"key": "pollDelayMs", "value": "1000", "type": "string"},
            {"key": "maxPollAttempts", "value": "60", "type": "string"},
        ],
        "item": tree_items(tree),
    }


def evidence_request_item(record: dict[str, Any], variable: str) -> dict[str, Any]:
    target = record.get("url") or record.get("path")
    if not isinstance(target, str):
        raise RepositoryError("evidence request requires a path or url")
    url = target if target.startswith(("http://", "https://")) else f"{{{{{variable}}}}}/{target.lstrip('/')}"
    request = postman_request(record, url)
    description = str(record.get("notes", ""))
    if description:
        request["description"] = description
    return {"name": str(record.get("id", "request")), "request": request}


def generate_evidence() -> dict[str, Any]:
    server_folders = []
    variables = []
    for server_path in sorted((REPOSITORY_ROOT / "evidence").glob("*/server.json")):
        server = read_json(server_path)
        if not isinstance(server, dict):
            continue
        variable = server["base_url"]["variable"]
        variables.append(
            {"key": variable, "value": server["base_url"]["default"], "type": "string"}
        )
        request_items = []
        process_ids = set()
        for path in sorted((server_path.parent / "requests").glob("*/request.json")):
            record = read_json(path)
            if not isinstance(record, dict):
                continue
            request_items.append(evidence_request_item(record, variable))
            if isinstance(record.get("process_id"), str):
                process_ids.add(record["process_id"])
        description_items = [
            {
                "name": process_id,
                "request": {
                    "method": "GET",
                    "header": [{"key": "Accept", "value": "application/json"}],
                    "url": f"{{{{{variable}}}}}/processes/{process_id}",
                },
            }
            for process_id in sorted(process_ids)
        ]
        if request_items or description_items:
            server_folders.append(
                {
                    "name": server["id"],
                    "item": [
                        {"name": "requests", "item": request_items},
                        {"name": "process-descriptions", "item": description_items},
                    ],
                }
            )
    return {
        "info": {
            "_postman_id": collection_id("evidence-requests"),
            "name": "OGC API Processes evidence requests",
            "description": "Generated from evidence/*/requests. Do not edit by hand.",
            "schema": COLLECTION_SCHEMA,
        },
        "variable": variables,
        "item": server_folders,
    }


def write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    scenarios_path = (
        args.output_dir / "representative-scenarios.postman_collection.json"
    )
    evidence_path = args.output_dir / "evidence-requests.postman_collection.json"
    write(scenarios_path, generate_scenarios())
    write(evidence_path, generate_evidence())
    print(f"generated: {scenarios_path}")
    print(f"generated: {evidence_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
