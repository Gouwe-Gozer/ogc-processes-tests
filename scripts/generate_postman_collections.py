#!/usr/bin/env python3
"""Generate deployment probes and live client scenarios as Postman collections."""

from __future__ import annotations

import argparse
import copy
import http.client
import json
import re
import sys
import urllib.parse
import uuid
from pathlib import Path
from typing import Any

from support.repository import (
    REPOSITORY_ROOT,
    RepositoryError,
    deployment_variable,
    load_deployment,
    read_json,
    reference_path,
)


COLLECTION_SCHEMA = (
    "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--deployment",
        action="append",
        dest="deployments",
        help="include only this deployment ID (repeatable)",
    )
    parser.add_argument(
        "--deployments-dir",
        type=Path,
        default=REPOSITORY_ROOT / "deployments",
    )
    parser.add_argument(
        "--testcases-dir", type=Path, default=REPOSITORY_ROOT / "testcases"
    )
    parser.add_argument(
        "--output-dir", type=Path, default=REPOSITORY_ROOT / "generated/postman"
    )
    return parser.parse_args()


def collection_id(name: str) -> str:
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"https://github.com/Gouwe-Gozer/ogc-processes-tests#{name}",
        )
    )


def header_list(headers: dict[str, str]) -> list[dict[str, str]]:
    return [{"key": key, "value": value} for key, value in headers.items()]


def deployment_url(target: str, variable: str) -> str:
    base = "{{" + variable + "}}"
    if "{{baseUrl}}" in target:
        return target.replace("{{baseUrl}}", base)
    if target.startswith("/"):
        return base + target
    return target


def request_body(owner: Path, body_file: object) -> dict[str, Any] | None:
    if body_file is None:
        return None
    if not isinstance(body_file, str):
        raise RepositoryError(f"{owner}: body_file must be a string")
    path = reference_path(owner, body_file)
    raw = path.read_text(encoding="utf-8")
    language = "json" if path.suffix == ".json" else "text"
    return {
        "mode": "raw",
        "raw": raw,
        "options": {"raw": {"language": language}},
    }


def postman_request(
    descriptor: dict[str, Any], descriptor_path: Path, variable: str
) -> dict[str, Any]:
    method = descriptor.get("method")
    target = descriptor.get("url") or descriptor.get("path")
    headers = descriptor.get("headers", {})
    if method not in {"GET", "POST", "DELETE"} or not isinstance(target, str):
        raise RepositoryError(f"{descriptor_path}: invalid method or URL")
    if not isinstance(headers, dict):
        raise RepositoryError(f"{descriptor_path}: headers must be an object")
    result: dict[str, Any] = {
        "method": method,
        "header": header_list(headers),
        "url": deployment_url(target, variable),
    }
    body = request_body(descriptor_path, descriptor.get("body_file"))
    if body is not None:
        result["body"] = body
    return result


def response_example(
    response_path: Path, original_request: dict[str, Any], variable: str
) -> dict[str, Any]:
    descriptor = read_json(response_path)
    if not isinstance(descriptor, dict) or not isinstance(descriptor.get("status"), int):
        raise RepositoryError(f"{response_path}: invalid response descriptor")
    headers = descriptor.get("headers", {})
    if not isinstance(headers, dict):
        raise RepositoryError(f"{response_path}: headers must be an object")
    body = ""
    body_file = descriptor.get("body_file")
    if isinstance(body_file, str):
        body = reference_path(response_path, body_file).read_text(
            encoding="utf-8", errors="replace"
        )
    deployment_base = "{{" + variable + "}}"
    body = body.replace("{{baseUrl}}", deployment_base)
    headers = {
        key: value.replace("{{baseUrl}}", deployment_base)
        for key, value in headers.items()
    }
    status = descriptor["status"]
    content_type = next(
        (value for key, value in headers.items() if key.lower() == "content-type"),
        "",
    )
    return {
        "name": f"Representative HTTP {status}",
        "originalRequest": copy.deepcopy(original_request),
        "status": http.client.responses.get(status, "Recorded response"),
        "code": status,
        "_postman_previewlanguage": "json" if "json" in content_type else "text",
        "header": header_list(headers),
        "cookie": [],
        "body": body,
    }


def load_deployments(
    deployments_dir: Path, selected: list[str] | None
) -> dict[str, tuple[dict[str, Any], Path]]:
    ids = selected or sorted(
        path.parent.name for path in deployments_dir.glob("*/deployment.json")
    )
    if not ids:
        raise RepositoryError(f"no deployment manifests found below {deployments_dir}")
    return {
        deployment_id: load_deployment(deployment_id, deployments_dir)
        for deployment_id in ids
    }


def probe_item(
    probe: dict[str, Any], probe_path: Path, variable: str
) -> dict[str, Any]:
    descriptor = probe.get("request")
    if not isinstance(descriptor, dict):
        raise RepositoryError(f"{probe_path}: request must be an object")
    request = postman_request(descriptor, probe_path, variable)
    description = [str(probe.get("title", probe.get("id", probe_path.parent.name)))]
    if probe.get("notes"):
        description.append(str(probe["notes"]))
    description.append(f"Canonical source: {probe_path.relative_to(REPOSITORY_ROOT)}")
    request["description"] = "\n\n".join(description)
    return {"name": str(probe.get("id", probe_path.parent.name)), "request": request}


def description_item(
    process_id: str, variable: str, source_names: list[str]
) -> dict[str, Any]:
    return {
        "name": process_id,
        "request": {
            "method": "GET",
            "header": [{"key": "Accept", "value": "application/json"}],
            "url": (
                "{{"
                + variable
                + "}}/processes/"
                + urllib.parse.quote(process_id, safe="")
            ),
            "description": "Descriptions for probes: " + ", ".join(source_names),
        },
    }


def generate_probe_collection(
    deployments: dict[str, tuple[dict[str, Any], Path]]
) -> dict[str, Any]:
    deployment_folders = []
    variables = []
    for deployment_id, (manifest, deployment_dir) in deployments.items():
        probes_name = manifest.get("probes")
        if not isinstance(probes_name, str):
            continue
        probe_paths = sorted((deployment_dir / probes_name).glob("*/probe.json"))
        if not probe_paths:
            continue
        variable = deployment_variable(manifest)
        variables.append(
            {"key": variable, "value": manifest["base_url"]["default"], "type": "string"}
        )
        sync_items: list[dict[str, Any]] = []
        async_items: list[dict[str, Any]] = []
        explicit_descriptions: list[dict[str, Any]] = []
        process_sources: dict[str, list[str]] = {}
        for probe_path in probe_paths:
            probe = read_json(probe_path)
            if not isinstance(probe, dict) or probe.get("status") == "pending":
                continue
            item = probe_item(probe, probe_path, variable)
            request = probe.get("request", {})
            method = request.get("method") if isinstance(request, dict) else None
            if method == "GET":
                explicit_descriptions.append(item)
            elif probe.get("execution_mode") == "async":
                async_items.append(item)
            else:
                sync_items.append(item)
            if method == "POST" and isinstance(probe.get("process_id"), str):
                process_sources.setdefault(probe["process_id"], []).append(probe["id"])
        descriptions = [
            description_item(process_id, variable, process_sources[process_id])
            for process_id in sorted(process_sources, key=str.casefold)
        ]
        deployment_folders.append(
            {
                "name": deployment_id,
                "item": [
                    {"name": "POST_process_sync", "item": sync_items},
                    {"name": "POST_process_async", "item": async_items},
                    {"name": "process_descriptions", "item": descriptions},
                    {
                        "name": "GET_process_description_cases",
                        "item": explicit_descriptions,
                    },
                ],
            }
        )
    return {
        "info": {
            "_postman_id": collection_id("deployment-probes"),
            "name": "OGC API Processes deployment probes",
            "description": "Generated from deployments/*/probes. Do not edit by hand.",
            "schema": COLLECTION_SCHEMA,
        },
        "variable": variables,
        "item": deployment_folders,
    }


def scenario_folder(
    testcase: dict[str, Any], testcase_path: Path, variable: str
) -> dict[str, Any]:
    items = []
    for step in testcase.get("steps", []):
        request_name = step.get("request")
        if not isinstance(request_name, str):
            raise RepositoryError(f"{testcase_path}: step request must be a string")
        request_path = testcase_path.parent / request_name
        descriptor = read_json(request_path)
        if not isinstance(descriptor, dict):
            raise RepositoryError(f"{request_path}: expected an object")
        request = postman_request(descriptor, request_path, variable)
        behavior = step.get("expected_client_behavior", {})
        must = behavior.get("must", []) if isinstance(behavior, dict) else []
        if must:
            request["description"] = "Preferred client behaviour:\n- " + "\n- ".join(must)
        item: dict[str, Any] = {"name": str(step.get("id", request_path.stem)), "request": request}
        response_name = step.get("representative_response")
        if isinstance(response_name, str):
            item["response"] = [
                response_example(
                    testcase_path.parent / response_name, request, variable
                )
            ]
        items.append(item)
    return {
        "name": testcase_path.parent.name,
        "description": str(testcase.get("title", testcase.get("id", ""))),
        "item": items,
    }


def generate_scenario_collection(
    deployments: dict[str, tuple[dict[str, Any], Path]], testcases_dir: Path
) -> dict[str, Any]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = {}
    used_deployments: set[str] = set()
    for testcase_path in sorted(testcases_dir.rglob("testcase.json")):
        testcase = read_json(testcase_path)
        if not isinstance(testcase, dict) or testcase.get("execution") != "live-capable":
            continue
        deployment_id = testcase.get("deployment")
        if deployment_id not in deployments:
            continue
        category = str(testcase.get("category", "uncategorized"))
        manifest = deployments[deployment_id][0]
        variable = deployment_variable(manifest)
        grouped.setdefault(deployment_id, {}).setdefault(category, []).append(
            scenario_folder(testcase, testcase_path, variable)
        )
        used_deployments.add(deployment_id)

    items = []
    for deployment_id in sorted(grouped):
        categories = [
            {"name": category, "item": grouped[deployment_id][category]}
            for category in sorted(grouped[deployment_id])
        ]
        items.append({"name": deployment_id, "item": categories})
    variables = [
        {
            "key": deployment_variable(deployments[deployment_id][0]),
            "value": deployments[deployment_id][0]["base_url"]["default"],
            "type": "string",
        }
        for deployment_id in sorted(used_deployments)
    ]
    serialized = json.dumps(items)
    deployment_vars = {entry["key"] for entry in variables}
    dynamic = sorted(
        set(re.findall(r"\{\{([A-Za-z][A-Za-z0-9]*)\}\}", serialized))
        - deployment_vars
    )
    variables.extend({"key": name, "value": "", "type": "string"} for name in dynamic)
    return {
        "info": {
            "_postman_id": collection_id("client-scenarios"),
            "name": "OGC API Processes live client scenarios",
            "description": (
                "Generated from live-capable testcases. Representative responses "
                "are examples; lifecycle variables must be captured while running."
            ),
            "schema": COLLECTION_SCHEMA,
        },
        "variable": variables,
        "item": items,
    }


def write_collection(path: Path, collection: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(collection, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> int:
    args = parse_args()
    try:
        deployments = load_deployments(args.deployments_dir, args.deployments)
        probes = generate_probe_collection(deployments)
        scenarios = generate_scenario_collection(deployments, args.testcases_dir)
        probe_path = args.output_dir / "deployment-probes.postman_collection.json"
        scenario_path = args.output_dir / "client-scenarios.postman_collection.json"
        write_collection(probe_path, probes)
        write_collection(scenario_path, scenarios)
    except (OSError, RepositoryError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"generated: {probe_path}")
    print(f"generated: {scenario_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
