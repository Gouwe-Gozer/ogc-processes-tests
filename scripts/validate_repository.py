#!/usr/bin/env python3
"""Validate deployment probes, client scenarios, and all referenced files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from support.repository import REPOSITORY_ROOT


KNOWN_VARIABLES = {"baseUrl", "jobUrl", "jobId", "resultUrl", "resultsUrl"}
VALID_METHODS = {"GET", "POST", "DELETE"}
VALID_EXECUTIONS = {"live-capable", "manual-only", "recorded-only"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-suite",
        action="store_true",
        help="rebuild testcases/suite.json before validating",
    )
    return parser.parse_args()


def suite_cases(root: Path) -> list[dict[str, Any]]:
    cases = []
    testcases_dir = root / "testcases"
    for path in sorted(testcases_dir.rglob("testcase.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        item = {
            "id": document["id"],
            "path": str(path.relative_to(testcases_dir)),
            "category": document["category"],
            "execution": document["execution"],
        }
        for key in ("deployment", "process_id"):
            if key in document:
                item[key] = document[key]
        cases.append(item)
    return cases


def write_suite(root: Path) -> None:
    cases = suite_cases(root)
    document = {
        "id": "ogc-processes-client-protocol-suite",
        "title": "OGC API Processes client protocol scenarios",
        "description": (
            "Behavior-oriented scenarios. Deployment-specific evidence is "
            "referenced but not duplicated."
        ),
        "case_count": len(cases),
        "cases": cases,
    }
    path = root / "testcases/suite.json"
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(cases)} cases to {path.relative_to(root)}")


class Validator:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.errors: list[str] = []
        self.json_documents = 0
        self.probes = 0
        self.testcases = 0

    def error(self, path: Path, message: str) -> None:
        try:
            display = path.relative_to(self.root)
        except ValueError:
            display = path
        self.errors.append(f"{display}: {message}")

    def read_json(self, path: Path) -> Any | None:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            self.error(path, f"invalid JSON: {error}")
            return None
        self.json_documents += 1
        return value

    def file_reference(self, owner: Path, reference: object, label: str) -> Path | None:
        if not isinstance(reference, str):
            self.error(owner, f"{label} must be a string")
            return None
        target = (owner.parent / reference).resolve()
        if not target.is_file():
            self.error(owner, f"{label} does not exist: {reference}")
            return None
        return target

    def request_descriptor(self, owner: Path, request: object) -> None:
        if not isinstance(request, dict):
            self.error(owner, "request descriptor must be an object")
            return
        if request.get("method") not in VALID_METHODS:
            self.error(owner, "request method must be GET, POST, or DELETE")
        target = request.get("url") or request.get("path")
        if not isinstance(target, str):
            self.error(owner, "request must contain a string url or path")
        headers = request.get("headers", {})
        if not isinstance(headers, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in headers.items()
        ):
            self.error(owner, "headers must map strings to strings")
        if "body_file" in request:
            self.file_reference(owner, request["body_file"], "body_file")

    def response_descriptor(self, owner: Path, response: object) -> None:
        if not isinstance(response, dict):
            self.error(owner, "response descriptor must be an object")
            return
        if not isinstance(response.get("status"), int):
            self.error(owner, "response status must be an integer")
        headers = response.get("headers", {})
        if not isinstance(headers, dict):
            self.error(owner, "response headers must be an object")
        if "body_file" in response:
            self.file_reference(owner, response["body_file"], "body_file")

    def validate_deployments(self) -> set[str]:
        deployment_ids: set[str] = set()
        for path in sorted((self.root / "deployments").glob("*/deployment.json")):
            document = self.read_json(path)
            if not isinstance(document, dict):
                self.error(path, "deployment manifest must be an object")
                continue
            deployment_id = path.parent.name
            deployment_ids.add(deployment_id)
            if document.get("id") != deployment_id:
                self.error(path, "id must match its directory name")
            base_url = document.get("base_url")
            if not isinstance(base_url, dict) or not all(
                isinstance(base_url.get(field), str)
                for field in ("variable", "default")
            ):
                self.error(path, "base_url requires string variable and default values")
        return deployment_ids

    def validate_probes(self, deployment_ids: set[str]) -> None:
        for path in sorted((self.root / "deployments").glob("*/probes/*/probe.json")):
            self.probes += 1
            document = self.read_json(path)
            if not isinstance(document, dict):
                self.error(path, "probe manifest must be an object")
                continue
            if document.get("id") != path.parent.name:
                self.error(path, "id must match its directory name")
            deployment = document.get("deployment")
            if deployment != path.parents[2].name or deployment not in deployment_ids:
                self.error(path, "deployment must match the owning deployment directory")
            self.request_descriptor(path, document.get("request"))
            expected = document.get("expected", {}).get("http_status")
            statuses = expected if isinstance(expected, list) else [expected]
            if not statuses or not all(isinstance(status, int) for status in statuses):
                self.error(path, "expected.http_status must be an integer or integer list")
            if "fixture" in document:
                self.file_reference(path, document["fixture"], "fixture")

    def validate_testcases(self, deployment_ids: set[str]) -> list[dict[str, Any]]:
        found: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for path in sorted((self.root / "testcases").rglob("testcase.json")):
            self.testcases += 1
            document = self.read_json(path)
            if not isinstance(document, dict):
                self.error(path, "testcase manifest must be an object")
                continue
            case_id = document.get("id")
            if not isinstance(case_id, str):
                self.error(path, "id must be a string")
            elif case_id in seen_ids:
                self.error(path, f"duplicate testcase id: {case_id}")
            else:
                seen_ids.add(case_id)
            category = path.parent.parent.name
            if document.get("category") != category:
                self.error(path, f"category must match directory {category!r}")
            if document.get("execution") not in VALID_EXECUTIONS:
                self.error(path, "execution has an unknown value")
            deployment = document.get("deployment")
            if deployment is not None and deployment not in deployment_ids:
                self.error(path, f"unknown deployment: {deployment}")
            steps = document.get("steps")
            if not isinstance(steps, list) or not steps:
                self.error(path, "steps must be a non-empty list")
                continue
            for step in steps:
                if not isinstance(step, dict):
                    self.error(path, "each step must be an object")
                    continue
                request_path = self.file_reference(path, step.get("request"), "step request")
                if request_path is not None:
                    self.request_descriptor(request_path, self.read_json(request_path))
                response_path = self.file_reference(
                    path, step.get("representative_response"), "representative response"
                )
                if response_path is not None:
                    self.response_descriptor(response_path, self.read_json(response_path))
            self.validate_relative_references(path, document)
            item = {
                "id": case_id,
                "path": str(path.relative_to(self.root / "testcases")),
                "category": document.get("category"),
                "execution": document.get("execution"),
            }
            for key in ("deployment", "process_id"):
                if key in document:
                    item[key] = document[key]
            found.append(item)
        return found

    def validate_relative_references(self, owner: Path, value: Any) -> None:
        if isinstance(value, dict):
            for child in value.values():
                self.validate_relative_references(owner, child)
        elif isinstance(value, list):
            for child in value:
                self.validate_relative_references(owner, child)
        elif isinstance(value, str) and value.startswith("../"):
            self.file_reference(owner, value, "relative reference")

    def validate_suite(self, found: list[dict[str, Any]]) -> None:
        path = self.root / "testcases/suite.json"
        suite = self.read_json(path)
        if not isinstance(suite, dict) or not isinstance(suite.get("cases"), list):
            self.error(path, "suite must contain a cases list")
            return
        if suite["cases"] != found:
            self.error(path, "case index is stale; regenerate it from testcase.json files")
        if suite.get("case_count") != len(found):
            self.error(path, "case_count does not match the indexed testcase count")

    def validate_all_json_and_variables(self) -> None:
        variable_pattern = re.compile(r"\{\{([A-Za-z][A-Za-z0-9]*)\}\}")
        for path in sorted(self.root.rglob("*.json")):
            if ".git" in path.parts or "__pycache__" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as error:
                self.error(path, f"cannot read text: {error}")
                continue
            try:
                json.loads(text)
            except json.JSONDecodeError as error:
                self.error(path, f"invalid JSON: {error}")
            for variable in variable_pattern.findall(text):
                if variable not in KNOWN_VARIABLES and "generated" not in path.parts:
                    self.error(path, f"unknown template variable: {variable}")

    def validate_markdown_links(self) -> None:
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for path in sorted(self.root.rglob("*.md")):
            if ".git" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as error:
                self.error(path, f"cannot read text: {error}")
                continue
            for target in link_pattern.findall(text):
                target = target.strip("<>").split("#", 1)[0]
                if not target or target.startswith(("http://", "https://", "mailto:")):
                    continue
                resolved = (path.parent / target).resolve()
                if not resolved.exists():
                    self.error(path, f"broken local Markdown link: {target}")

    def run(self) -> int:
        deployment_ids = self.validate_deployments()
        self.validate_probes(deployment_ids)
        found = self.validate_testcases(deployment_ids)
        self.validate_suite(found)
        self.validate_all_json_and_variables()
        self.validate_markdown_links()
        if self.errors:
            for error in self.errors:
                print(f"error: {error}", file=sys.stderr)
            print(f"validation failed with {len(self.errors)} error(s)", file=sys.stderr)
            return 1
        print(
            f"validated {len(deployment_ids)} deployments, {self.probes} probes, "
            f"{self.testcases} client testcases"
        )
        return 0


def main() -> int:
    args = parse_args()
    if args.write_suite:
        try:
            write_suite(REPOSITORY_ROOT)
        except (OSError, KeyError, json.JSONDecodeError) as error:
            print(f"error: unable to write suite: {error}", file=sys.stderr)
            return 2
    return Validator(REPOSITORY_ROOT).run()


if __name__ == "__main__":
    raise SystemExit(main())
