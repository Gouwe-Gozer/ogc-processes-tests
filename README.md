# OGC API Processes examples

This repository collects representative OGC API Processes requests and
responses that our client should be able to handle.

Start with [`examples/`](examples/). It contains a small, readable set for
client implementation and tests. [`evidence/`](evidence/) contains the larger
collection of provider-specific requests, responses, and process descriptions
that led to those choices.

The files are test data. They do not test a client by themselves. Actual
assertions belong in the client project's normal TypeScript test suite.

## Folder guide

| Folder | Contents |
|---|---|
| `examples/` | Small representative request-response exchanges |
| `evidence/` | Runnable provider requests and captured responses kept for reference |
| `fixtures/` | Small raster, vector, table, and point-cloud input files |
| `scripts/` | Commands for running evidence requests and updating captures |
| `generated/postman/` | Postman collections generated from `examples/` and `evidence/` |
| `docs/` | Client scope, lessons learned, and example-selection notes |

An example contains complete HTTP request and response records. An evidence
request records one exact request for one server, including why it was kept and
the status observed during testing.

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

This command saves a process description, response status, headers, and final
URL under `evidence/zoo-local/responses/descriptions/`:

```bash
python3 scripts/capture_process_descriptions.py hellojs Buffer
```

## Generate Postman collections

```bash
python3 scripts/generate_postman_collections.py
```

The generated files are written to [`generated/postman/`](generated/postman/).

## Documentation

- [`docs/client-core.md`](docs/client-core.md): features that belong in the
  OGC API Processes client library.
- [`docs/client-behaviour.md`](docs/client-behaviour.md): information from
  process descriptions and handling of bad input or responses.
- [`docs/test-strategy.md`](docs/test-strategy.md): how representative examples
  are selected and used.
- [`docs/deployment-compatibility.md`](docs/deployment-compatibility.md): why
  results differ between servers and software versions.
- [`evidence/zoo-local/README.md`](evidence/zoo-local/README.md): details about
  the local ZOO evidence.

## Editing the repository

- Keep the main `examples/` set small. Add an example only when it introduces
  a different input, output, job flow, or error shape.
- Put similar processes and provider-specific details under `evidence/`.
- Keep raw error bodies. Exact server messages can help explain failures.
- Regenerate the Postman collections after changing examples, evidence
  requests, or server URLs.
