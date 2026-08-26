"""Load deployment, probe, and request metadata from the repository."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class RepositoryError(ValueError):
    """Raised when repository metadata is missing or malformed."""


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RepositoryError(f"cannot read JSON from {path}: {error}") from error


def load_deployment(
    deployment_id: str, deployments_dir: Path | None = None
) -> tuple[dict[str, Any], Path]:
    base = deployments_dir or REPOSITORY_ROOT / "deployments"
    deployment_dir = base / deployment_id
    manifest_path = deployment_dir / "deployment.json"
    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict):
        raise RepositoryError(f"{manifest_path} must contain a JSON object")
    if manifest.get("id") != deployment_id:
        raise RepositoryError(
            f"{manifest_path}: id must match directory name {deployment_id!r}"
        )
    base_url = manifest.get("base_url")
    if not isinstance(base_url, dict) or not isinstance(base_url.get("default"), str):
        raise RepositoryError(f"{manifest_path}: base_url.default must be a string")
    return manifest, deployment_dir


def deployment_base_url(manifest: dict[str, Any], override: str | None = None) -> str:
    value = override or manifest["base_url"]["default"]
    return value.rstrip("/")


def deployment_variable(manifest: dict[str, Any]) -> str:
    variable = manifest.get("base_url", {}).get("variable")
    if not isinstance(variable, str) or not variable:
        raise RepositoryError("base_url.variable must be a non-empty string")
    return variable


def resolve_url(target: str, base_url: str) -> str:
    """Resolve a repository URL template or relative API path."""
    if "{{baseUrl}}" in target:
        return target.replace("{{baseUrl}}", base_url)
    if target.startswith(("http://", "https://")):
        return target
    if "{{" in target:
        raise RepositoryError(f"URL contains an unresolved variable: {target}")
    return f"{base_url}/{target.lstrip('/')}"


def reference_path(owner: Path, reference: str) -> Path:
    """Resolve a file reference relative to the JSON document that owns it."""
    return (owner.parent / reference).resolve()
