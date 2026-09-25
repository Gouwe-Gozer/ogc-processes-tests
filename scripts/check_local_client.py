"""Check this suite against a sibling OAP client compiled in a disposable directory."""

import argparse
import json
import os
import shutil
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
    if manifest.get("dependencies") or manifest.get("optionalDependencies"):
        parser.error("The local core now has runtime dependencies. This isolated compiler supports the dependency-free core only.")
    exports = manifest["exports"]["."]
    if exports != {"types": "./dist/index.d.ts", "default": "./dist/index.js"}:
        parser.error("The core export layout has changed; update the isolated build before testing it.")
    for required in [core / "src/index.ts", core / "tsconfig.json", checkout / "tsconfig.base.json"]:
        if not required.is_file():
            parser.error(f"Required client source/configuration is missing: {required}")
    compiler = REPOSITORY / "node_modules/typescript/bin/tsc"
    runner = REPOSITORY / "node_modules/vitest/vitest.mjs"
    if not compiler.is_file() or not runner.is_file():
        parser.error("Test tools are missing. Run npm ci in ogc-processes-tests first.")
    print(f"Client: LOCAL source, version {manifest['version']}", flush=True)
    print(f"Read-only source: {core}", flush=True)
    with tempfile.TemporaryDirectory(prefix="oap-client-check-") as temporary:
        snapshot = Path(temporary)
        built_core = snapshot / "packages/core"
        built_core.mkdir(parents=True)
        # Copy only what the dependency-free core needs. Its own settings apply,
        # but compiler outputs and all relative paths stay inside this snapshot.
        shutil.copytree(core / "src", built_core / "src")
        shutil.copyfile(manifest_path, built_core / "package.json")
        shutil.copyfile(core / "tsconfig.json", built_core / "tsconfig.json")
        shutil.copyfile(checkout / "tsconfig.base.json", snapshot / "tsconfig.base.json")
        build_project = built_core / "tsconfig.recorded-tests.json"
        build_project.write_text(json.dumps({
            "extends": "./tsconfig.json",
            "compilerOptions": {
                "rootDir": "./src", "outDir": "./dist",
                "composite": False, "incremental": False, "noEmit": False,
                "noEmitOnError": True, "declaration": True,
                "declarationMap": False, "sourceMap": False,
            },
            "include": ["src/**/*.ts"], "exclude": [],
        }))
        print("Compiling a temporary source copy with this suite's TypeScript compiler...", flush=True)
        compiled = subprocess.run(
            ["node", str(compiler), "--project", str(build_project)],
            cwd=snapshot, check=False,
        )
        if compiled.returncode:
            return compiled.returncode
        declarations = built_core / "dist/index.d.ts"
        # TypeScript checks the new declarations; Vitest imports the new JS.
        config = {
            "extends": str(REPOSITORY / "tsconfig.json"),
            "compilerOptions": {
                "paths": {PACKAGE: [str(declarations)]},
                "typeRoots": [str(REPOSITORY / "node_modules/@types")],
            },
        }
        environment = {**os.environ, "OAP_TEST_CLIENT_DIR": str(built_core)}
        project = snapshot / "tsconfig.tests.json"
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
