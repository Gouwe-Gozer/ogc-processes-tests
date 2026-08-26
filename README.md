# OGC API Processes tests

This repository contains requests and example responses for testing an OGC API
- Processes client. Most live requests use a local ZOO-Project server. Two
recorded pygeoapi examples cover other response shapes.

## Before you start

Clone the [ZOO-Project fork used for these tests](https://github.com/Gouwe-Gozer/ZOO-Project),
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

Open another terminal and go to this repository before running the commands
below.

## Quick start

Check that all JSON files and file links are valid:

```bash
python3 scripts/validate_repository.py
```

Print a request as a `curl` command:

```bash
python3 scripts/run_probe.py hellojs_string --print-curl
```

Send that request to the local ZOO server:

```bash
python3 scripts/run_probe.py hellojs_string
```

The runner reads the URL from `deployments/zoo-local/deployment.json`. Use
`--base-url` to send the same request to another URL:

```bash
python3 scripts/run_probe.py hellojs_string \
  --base-url https://demo-ets.geolabs.fr/ogc-api
```

### Processes that need files inside the ZOO container

Some GDAL and OGR processes expect a filename on the server. Copy the test
fixtures into the running container before testing those processes:

```bash
python3 scripts/deployments/stage_zoo_fixtures.py --dry-run
python3 scripts/deployments/stage_zoo_fixtures.py
```

The default container name is `zoo-project-zoofpm-1`. If Docker Compose uses a
different name, pass it with `--container`.

### Capture process descriptions

This command saves the response body, HTTP status, headers, and final URL:

```bash
python3 scripts/capture_process_descriptions.py hellojs Buffer
```

### Generate Postman collections

```bash
python3 scripts/generate_postman_collections.py
```

The generated files are written to `generated/postman/`.

## Folder guide

| Folder | Contents |
|---|---|
| `deployments/` | Server URLs, runnable requests, and responses captured from each server |
| `testcases/` | Expected client behavior for successful and unsuccessful responses |
| `fixtures/` | Small raster, vector, table, and point-cloud input files |
| `scripts/` | Commands for running requests, capturing responses, and generating files |
| `generated/postman/` | Generated Postman collections |
| `docs/` | Notes for implementing and testing the client |

A **probe** is an exact request sent to one server. A **testcase** describes how
the client should handle a request and response. Several testcases refer to the
same probe or captured response.

## Documentation

- [`docs/client-core.md`](docs/client-core.md): which features belong in the
  OGC API Processes client library.
- [`docs/client-behaviour.md`](docs/client-behaviour.md): what the client can
  learn from process descriptions and how it should handle bad input or bad
  responses.
- [`docs/test-strategy.md`](docs/test-strategy.md): which processes and error
  cases are useful for client testing.
- [`docs/deployment-compatibility.md`](docs/deployment-compatibility.md): why
  results can differ between servers and software versions.
- [`deployments/zoo-local/README.md`](deployments/zoo-local/README.md): details
  about the local ZOO test server.

## Editing the repository

- Edit probes and testcases, not the generated Postman JSON.
- Run `python3 scripts/validate_repository.py --write-suite` after adding or
  moving a testcase.
- Run `python3 scripts/generate_postman_collections.py` after changing a probe,
  testcase, or deployment URL.
- Keep the raw response body when adding an error example. The exact server
  message may help explain a later failure.
