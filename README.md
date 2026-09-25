# OGC API Processes scenarios

This repository has two connected purposes:

- **Collect real input and output examples for the client and its UI.** Preserve
  process descriptions, execution requests and responses with varied payloads:
  numbers, arrays, GeoJSON, CSV, nested JSON, files and download links. These
  examples help colleagues build forms, encode requests and present results.
- **Test the real client core against selected recorded conversations.** The
  suite under [`tests/`](tests/) checks the requests the client builds and how
  it interprets discovery, execution, job and error responses.

Start with [`scenarios/`](scenarios/): [`forms/`](scenarios/forms/) connects input
schemas to request bodies; [`results/`](scenarios/results/) connects output
schemas to returned values; `protocol/` covers the HTTP conversations.
[`evidence/`](evidence/) keeps the fuller captures and their provenance.
A useful UI example does not need an executable test here to belong in the repo.

The `oap-client` repository owns the implementation and its own core unit,
web UI, relay, browser and live-provider tests. Our suite complements those
with real provider recordings. Neither of our test commands runs that other
repository's tests or proves that its UI works in a browser. See the
[division of responsibilities](docs/test-strategy.md#which-repository-tests-what).

The end goal, current limits, and decisions that wait for the client are
documented in [`docs/test-strategy.md`](docs/test-strategy.md).

New to automated testing? Start with [Understanding the recorded client tests](docs/understanding-the-tests.md)
for a plain-language explanation of the real client, fake transporter and test files.

## Attending the plugfest

See [`plugfest/`](plugfest/) for practical instructions to collect new evidence,
probe visiting services and report reproducible problems, or reuse our local
APIs and recordings with another company's client.

## Run the client tests

With Node 24 or later:

```bash
npm ci
npm run check
```

This runs TypeScript checking and the deterministic Vitest suite. No live
provider or sibling client checkout is needed. GitHub Actions runs the same
commands on pushes and pull requests. See the
[test suite guide](docs/client-fixture-handoff.md) for coverage, fixture
conversion, and the distinction between recorded tests and live compatibility.

To test source from the sibling `../oap-client` checkout instead:

```bash
npm run check:local
```

This requires Python 3. It copies and compiles the client in a temporary folder,
then checks both types and behaviour. It leaves the client checkout and installed
dependencies untouched. See the
[local client instructions](docs/client-fixture-handoff.md#test-a-local-client-build).

## Folder guide

| Folder | Contents |
|---|---|
| `scenarios/` | Small representative request-response exchanges |
| `evidence/` | Provider captures grouped by discovery, descriptions, executions, and jobs |
| `tests/` | Executable cross-provider tests of the real client and a small recorded fetch |
| `fixtures/` | Small raster, vector, table, and point-cloud input files |
| `scripts/` | Commands for running evidence requests and updating captures |
| `generated/postman/` | Postman collections generated from `scenarios/` and `evidence/` |
| `plugfest/` | Event preparation, manual client/server checklist and results template |
| `docs/` | Client scope, lessons learned, and scenario-selection notes |

A scenario contains representative material reusable across client tests. Evidence
keeps each provider request beside the response that was actually observed.
Complete evidence records the response status, headers, final URL, and body.

## Before running ZOO requests

Clone the [ZOO-Project fork used for these requests](https://github.com/Gouwe-Gozer/ZOO-Project),
then build and start its containers:

```bash
git clone https://github.com/Gouwe-Gozer/ZOO-Project.git
cd ZOO-Project
mkdir -p docker/tmp
chmod 777 docker/tmp
docker-compose up
```

Keep that command running. The local API should become available at
`http://localhost/ogc-api`.

## Run an evidence request

Print a stored request as `curl`:

```bash
python3 scripts/run_evidence_request.py hellojs_string --print-curl
```

Send it to the local ZOO server:

```bash
python3 scripts/run_evidence_request.py hellojs_string
```

Add or replace the matching complete `response.json`:

```bash
python3 scripts/run_evidence_request.py hellojs_string --save-response
```

The command reads the default URL from
[`evidence/zoo-local/server.json`](evidence/zoo-local/server.json). Override it
when needed:

```bash
python3 scripts/run_evidence_request.py hellojs_string \
  --base-url https://demo-ets.geolabs.fr/ogc-api
```

### Requests that need files inside the ZOO container

Some older GDAL and OGR processes expect a filename inside the server. Copy the
fixtures into the local ZOO container before running those requests:

```bash
python3 scripts/stage_zoo_fixtures.py --dry-run
python3 scripts/stage_zoo_fixtures.py
```

This is local evidence infrastructure. A browser client does not stage files
inside a processing server.

## Update captured descriptions

This command saves the request, process description, response status, headers,
and final URL under `evidence/zoo-local/captures/descriptions/<process-id>/`:

```bash
python3 scripts/capture_process_descriptions.py hellojs Buffer
```

## Generate Postman collections

```bash
python3 scripts/generate_postman_collections.py
```

The generated files are written to [`generated/postman/`](generated/postman/).
Run the `protocol/jobs/zoo-local/successful-job` folder with Postman's
Collection Runner to run the full sequence. Its post-response scripts save the
job URL and ID, repeat the status request until the job finishes, and save the
results URL for the last request.

## Documentation

- [`docs/client-core.md`](docs/client-core.md): features that belong in the
  OGC API Processes client library.
- [`docs/client-behaviour.md`](docs/client-behaviour.md): information from
  process descriptions and handling of bad input or responses.
- [`docs/test-strategy.md`](docs/test-strategy.md): repository scope, scenario
  selection, and implemented versus pending client tests.
- [`docs/client-fixture-handoff.md`](docs/client-fixture-handoff.md): running
  the suite locally and in CI, fixture conversion, and adding tests.
- [`docs/deployment-compatibility.md`](docs/deployment-compatibility.md): why
  results differ between servers and software versions.
- [`evidence/zoo-local/README.md`](evidence/zoo-local/README.md): details about
  the local ZOO evidence.

## Editing the repository

- Keep the main `scenarios/` set small. Add a scenario only when it introduces
  a different input, output, job flow, or error shape.
- Put similar processes and provider-specific details under `evidence/`.
- Keep raw error bodies. Exact server messages can help explain failures.
- Regenerate the Postman collections after changing scenarios, evidence
  requests, or server URLs.
