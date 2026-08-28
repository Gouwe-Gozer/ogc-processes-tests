# OGC API Processes scenarios

This repository collects representative OGC API Processes requests and
responses that our client should be able to handle.

Start with [`scenarios/`](scenarios/). It contains a small, readable set intended
for future client implementation and tests. [`evidence/`](evidence/) contains
the larger collection of provider-specific requests, responses, and process
descriptions that led to those choices.

The files are test data. They do not test a client by themselves. Actual
assertions belong in the client project's normal TypeScript test suite.

The end goal, current limits, and decisions that wait for the client are
documented in [`docs/test-strategy.md`](docs/test-strategy.md).

## Folder guide

| Folder | Contents |
|---|---|
| `scenarios/` | Small representative request-response exchanges |
| `evidence/` | Provider captures grouped by discovery, descriptions, executions, and jobs |
| `fixtures/` | Small raster, vector, table, and point-cloud input files |
| `scripts/` | Commands for running evidence requests and updating captures |
| `generated/postman/` | Postman collections generated from `scenarios/` and `evidence/` |
| `docs/` | Client scope, lessons learned, and scenario-selection notes |

A scenario contains representative material for future client tests. Evidence
keeps each provider request beside the response that was actually observed.
Older incomplete captures are clearly marked until they can be rerun.

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
  selection, and the future client test suites.
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
