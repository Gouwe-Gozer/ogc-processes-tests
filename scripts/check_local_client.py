"""Check this suite against a prebuilt sibling OAP client without installing it."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = Path(__file__).resolve().parents[1]
PACKAGE = "@breinstein/oap-client"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--client", type=Path, default=REPOSITORY.parent / "oap-client",
        help="client checkout (default: ../oap-client beside this repository)",
    )
    args, test_arguments = parser.parse_known_args()
    checkout = args.client.resolve()
    core = checkout / "packages" / "core"
    manifest_path = core / "package.json"
    if not manifest_path.is_file():
        parser.error(f"No client package at {manifest_path}. Use --client PATH for another checkout.")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("name") != PACKAGE:
        parser.error(f"Expected {PACKAGE} in {manifest_path}.")
    exports = manifest["exports"]["."]
    entry = core / exports["default"]
    declarations = core / exports["types"]
    if not entry.is_file() or not declarations.is_file():
        parser.error(
            f"Local client build is missing in {core}.\n"
            f"In {checkout}, run:\n"
            "  pnpm install --frozen-lockfile\n"
            f"  pnpm --filter {PACKAGE} build\n"
            "Then rerun this command. The published client will not be used as a fallback."
        )
    compiler = REPOSITORY / "node_modules/typescript/bin/tsc"
    runner = REPOSITORY / "node_modules/vitest/vitest.mjs"
    if not compiler.is_file() or not runner.is_file():
        parser.error("Test tools are missing. Run npm ci in ogc-processes-tests first.")
    print(f"Client: LOCAL build, version {manifest['version']}", flush=True)
    print(f"Package: {core}", flush=True)
    print(f"JavaScript: {entry}", flush=True)
    print(f"Types: {declarations}", flush=True)
    print("This command does not rebuild the client. Rebuild after changing or pulling its source.", flush=True)
    # TypeScript checks the local declarations; Vitest aliases runtime imports.
    config = {
        "extends": str(REPOSITORY / "tsconfig.json"),
        "compilerOptions": {
            "paths": {PACKAGE: [str(declarations)]},
            "typeRoots": [str(REPOSITORY / "node_modules/@types")],
        },
    }
    environment = {**os.environ, "OAP_TEST_CLIENT_DIR": str(core)}
    with tempfile.TemporaryDirectory(prefix="oap-client-check-") as temporary:
        project = Path(temporary) / "tsconfig.json"
        project.write_text(json.dumps(config))
        checked = subprocess.run(
            ["node", str(compiler), "--project", str(project), "--noEmit"],
            cwd=REPOSITORY, env=environment, check=False,
        )
        if checked.returncode:
            return checked.returncode
        tested = subprocess.run(
            ["node", str(runner), "run", *test_arguments],
            cwd=REPOSITORY, env=environment, check=False,
        )
        return tested.returncode


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"Cannot check local client: {error}", file=sys.stderr)
        sys.exit(1)
