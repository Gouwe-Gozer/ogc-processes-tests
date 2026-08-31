#!/usr/bin/env python3
"""Generate the scenario collection and one evidence collection per provider."""

from __future__ import annotations

import argparse
import json
import re
import uuid
from pathlib import Path
from typing import Any

from support.repository import REPOSITORY_ROOT, RepositoryError, read_json


COLLECTION_SCHEMA = (
    "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
)
FOLDER_ORDER = {
    "protocol": 0,
    "forms": 1,
    "results": 2,
    "discovery": 10,
    "execution": 11,
    "descriptions": 11,
    "executions": 12,
    "jobs": 13,
    "errors": 14,
    "inputs": 15,
    "validation": 16,
    "maps": 20,
    "tables": 21,
    "values": 22,
    "downloads": 23,
}


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
        responses = [(None, response_path)] if response_path.is_file() else []
        for variant_path in sorted(request_path.parent.glob("*.response.json")):
            label = variant_path.name.removesuffix(".response.json")
            responses.append((label, variant_path))
        return responses

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


def collection_url(record: dict[str, Any], base_url_variable: str) -> str:
    target = record.get("url") or record.get("path")
    if not isinstance(target, str):
        raise RepositoryError("request requires a string path or url")
    if "{{baseUrl}}" in target:
        return target.replace("{{baseUrl}}", f"{{{{{base_url_variable}}}}}")
    if target.startswith(("http://", "https://", "{{")):
        return target
    return f"{{{{{base_url_variable}}}}}/{target.lstrip('/')}"


def collection_item(
    request_path: Path,
    base_url_variable: str,
    *,
    include_post_response: bool = True,
) -> dict[str, Any]:
    record = read_json(request_path)
    if not isinstance(record, dict):
        raise RepositoryError(f"{request_path} must contain an object")
    url = collection_url(record, base_url_variable)
    request = postman_request(record, url)
    notes = record.get("notes")
    if isinstance(notes, str) and notes:
        request["description"] = notes
    name = request_path.name.removesuffix(".request.json")
    item: dict[str, Any] = {"name": name, "request": request}
    response_examples = []
    for label, response_path in paired_responses(request_path):
        response = read_json(response_path)
        if isinstance(response, dict) and "body" in response:
            response_examples.append(response_example(response, request, label))
    if response_examples:
        item["response"] = response_examples
    if include_post_response:
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
    names = (key for key in tree if key != "__items__")
    for name in sorted(
        names,
        key=lambda value: (FOLDER_ORDER.get(value, 100), value),
    ):
        result.append({"name": name, "item": tree_items(tree[name])})
    return result


def evidence_tree_items(tree: dict[str, Any]) -> list[dict[str, Any]]:
    result = list(tree.get("__items__", []))
    names = (key for key in tree if key != "__items__")
    for name in sorted(
        names,
        key=lambda value: (FOLDER_ORDER.get(value, 100), value),
    ):
        child = tree[name]
        child_items = child.get("__items__", [])
        child_folders = [key for key in child if key != "__items__"]
        if len(child_items) == 1 and not child_folders:
            item = dict(child_items[0])
            item["name"] = name
            result.append(item)
        else:
            result.append({"name": name, "item": evidence_tree_items(child)})
    return result


def generate_scenarios() -> dict[str, Any]:
    root = REPOSITORY_ROOT / "scenarios"
    providers: dict[str, tuple[str, str]] = {}
    for server_path in sorted((REPOSITORY_ROOT / "evidence").glob("*/server.json")):
        server = read_json(server_path)
        if not isinstance(server, dict):
            continue
        base_url = server.get("base_url")
        if not isinstance(base_url, dict):
            continue
        providers[server_path.parent.name] = (
            str(base_url["variable"]),
            str(base_url["default"]),
        )

    request_paths = sorted(root.rglob("*.request.json"))
    tree: dict[str, Any] = {}
    for path in request_paths:
        relative = path.parent.relative_to(root)
        if len(relative.parts) < 2:
            raise RepositoryError(
                f"{path} must be stored below a provider and scenario folder"
            )
        provider = relative.parts[-2]
        if provider not in providers:
            raise RepositoryError(
                f"{path} uses provider {provider!r} without evidence/{provider}/server.json"
            )
        base_url_variable, _ = providers[provider]
        add_to_tree(
            tree,
            relative.parts,
            collection_item(path, base_url_variable),
        )

    used_providers = {
        path.parent.relative_to(root).parts[-2] for path in request_paths
    }
    provider_variables = [
        {"key": providers[name][0], "value": providers[name][1], "type": "string"}
        for name in sorted(used_providers)
    ]
    return {
        "info": {
            "_postman_id": collection_id("representative-scenarios"),
            "name": "OGC API Processes representative scenarios",
            "description": "Generated from scenarios/. Do not edit by hand.",
            "schema": COLLECTION_SCHEMA,
        },
        "variable": provider_variables + [
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


def template_variables(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    names = set()
    for record in records:
        names.update(
            re.findall(r"{{([A-Za-z][A-Za-z0-9_]*)}}", json.dumps(record))
        )
    names.discard("baseUrl")
    return [
        {"key": name, "value": "", "type": "string"}
        for name in sorted(names)
    ]


def generate_evidence(server_path: Path) -> dict[str, Any]:
    server = read_json(server_path)
    if not isinstance(server, dict):
        raise RepositoryError(f"{server_path} must contain an object")
    capture_root = server_path.parent / "captures"
    request_paths = sorted(capture_root.rglob("*request.json"))
    records = []
    tree: dict[str, Any] = {}
    for path in request_paths:
        record = read_json(path)
        if not isinstance(record, dict):
            raise RepositoryError(f"{path} must contain an object")
        records.append(record)
        add_to_tree(
            tree,
            path.parent.relative_to(capture_root).parts,
            collection_item(path, "baseUrl", include_post_response=False),
        )

    title = str(server.get("title") or server["id"])
    return {
        "info": {
            "_postman_id": collection_id(f"evidence-{server['id']}"),
            "name": f"OGC API Processes evidence — {title}",
            "description": (
                f"Generated from evidence/{server['id']}/captures. "
                "Do not edit by hand."
            ),
            "schema": COLLECTION_SCHEMA,
        },
        "variable": [
            {
                "key": "baseUrl",
                "value": server["base_url"]["default"],
                "type": "string",
            },
            *template_variables(records),
        ],
        "item": evidence_tree_items(tree),
    }


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    scenarios_path = (
        args.output_dir / "representative-scenarios.postman_collection.json"
    )
    write(scenarios_path, generate_scenarios())
    print(f"generated: {scenarios_path}")
    evidence_dir = args.output_dir / "evidence"
    for server_path in sorted((REPOSITORY_ROOT / "evidence").glob("*/server.json")):
        evidence_path = (
            evidence_dir
            / f"{server_path.parent.name}.postman_collection.json"
        )
        write(evidence_path, generate_evidence(server_path))
        print(f"generated: {evidence_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
