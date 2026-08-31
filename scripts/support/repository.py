"""Read server and HTTP exchange files from the repository."""

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


def load_server(
    server_id: str, evidence_dir: Path | None = None
) -> tuple[dict[str, Any], Path]:
    base = evidence_dir or REPOSITORY_ROOT / "evidence"
    server_dir = base / server_id
    manifest_path = server_dir / "server.json"
    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict):
        raise RepositoryError(f"{manifest_path} must contain a JSON object")
    if manifest.get("id") != server_id:
        raise RepositoryError(
            f"{manifest_path}: id must match directory name {server_id!r}"
        )
    base_url = manifest.get("base_url")
    if not isinstance(base_url, dict) or not isinstance(base_url.get("default"), str):
        raise RepositoryError(f"{manifest_path}: base_url.default must be a string")
    return manifest, server_dir


def server_base_url(manifest: dict[str, Any], override: str | None = None) -> str:
    value = override or manifest["base_url"]["default"]
    return value.rstrip("/")


def resolve_url(target: str, base_url: str) -> str:
    """Resolve a repository URL template or relative API path."""
    if "{{baseUrl}}" in target:
        return target.replace("{{baseUrl}}", base_url)
    if target.startswith(("http://", "https://")):
        return target
    if "{{" in target:
        raise RepositoryError(f"URL contains an unresolved variable: {target}")
    return f"{base_url}/{target.lstrip('/')}"


def response_header_map(headers: Any) -> dict[str, str]:
    """Return response headers without discarding repeated field values."""
    names: dict[str, str] = {}
    values: dict[str, list[str]] = {}
    for name, value in headers.items():
        key = name.lower()
        names.setdefault(key, name)
        values.setdefault(key, []).append(value)
    return {names[key]: ", ".join(items) for key, items in values.items()}
