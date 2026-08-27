# Local ZOO server

Most live requests in this repository use the local ZOO-Project server at
`http://localhost/ogc-api`. Follow the setup in the
[main README](../../README.md#before-running-zoo-requests) before running a
request.

The process list checked on 2026-08-24 contained 703 processes. This repository
keeps 53 requests for 50 selected process entries.

Software versions recorded for these responses:

```text
Ubuntu 18.04.6 LTS
GDAL 3.0.4
SAGA 7.3.0
OTB 7.x, with the ZOO adapter configured for 7.0
responses captured on 2026-08-25
```

## Files

- [`server.json`](server.json): base URL, container name, and fixture
  path.
- [`requests/`](requests/): runnable requests, including their headers and body.
- [`exchanges/`](exchanges/): complete request-response pairs kept for
  comparison and future tests.
- [`responses/descriptions/`](responses/descriptions/): process descriptions and
  the HTML error returned by `OTB.ReadImageInfo`.
- [`responses/executions/`](responses/executions/): execution and job response
  bodies.
- [`responses/catalogs/error-catalog.json`](responses/catalogs/error-catalog.json):
  all distinct server messages and what the client may safely say about them.
- [`responses/diagnostics/`](responses/diagnostics/): process-selection records
  and direct OTB command-line checks.

## Run a request

```bash
python3 scripts/run_evidence_request.py hellojs_string --print-curl
python3 scripts/run_evidence_request.py hellojs_string
```

To test the same request at another URL:

```bash
python3 scripts/run_evidence_request.py hellojs_string \
  --base-url https://example.org/ogc-api
```

## Copy fixtures into the container

Some GDAL and OGR processes expect a filename inside the ZOO container. Copy
the fixture files before running those requests:

```bash
python3 scripts/stage_zoo_fixtures.py --dry-run
python3 scripts/stage_zoo_fixtures.py
```

This is only needed for local testing. It is not something the browser client
will do for an end user.

## SAGA results

The 18 main SAGA requests returned:

- 11 usable results with HTTP 200;
- 2 HTTP 200 responses that omitted the requested output;
- 1 HTTP 200 response with a link to a file that did not exist;
- 4 HTTP 500 process crashes or aborts.

Three raster processes work with one input but return `SIGSEGV` when sent two
inputs through a field that the description says can be repeated.

These responses test two important client behaviors:

- a request can follow the description and still fail on the server;
- HTTP 200 does not guarantee that the requested output is present or usable.

## OTB results

Five OTB process descriptions load successfully. All five execution requests
return HTTP 500 with:

```text
No OTB Application found.
```

Direct OTB 7 command-line checks succeed with the same files and parameters.
The API error happens before the files are processed, so the client should not
tell the user that an input file is invalid.

`OTB.ReadImageInfo` fails earlier: its process-description endpoint returns an
HTML HTTP 500 response after the ZOO loader crashes. The client should mark
only that process as unavailable and keep the other process descriptions.

The OTB descriptions are still useful test data. They include repeated image
inputs, dotted input IDs, conditional fields, and an ID that appears in both
the input and output lists.
