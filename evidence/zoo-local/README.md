# Local ZOO server

Most ZOO captures use the local server at `http://localhost/ogc-api`. Follow
the setup in the [main README](../../README.md#before-running-zoo-requests)
before running a request.

The process list captured on 31 August 2026 contains 703 processes. The
repository keeps a smaller selection of execution, validation, and job
interactions from that deployment.

Software versions recorded with the original captures:

```text
Ubuntu 18.04.6 LTS
GDAL 3.0.4
SAGA 7.3.0
OTB 7.x, with the ZOO adapter configured for 7.0
responses captured on 25 August 2026
```

## Contents

- [`server.json`](server.json): base URL, container name, and fixture path.
- [`captures/discovery/`](captures/discovery/): landing page, conformance
  declaration, and complete process list.
- [`captures/descriptions/`](captures/descriptions/): one folder per process
  description.
- [`captures/executions/`](captures/executions/): successful, failed, and
  malformed execution results.
- [`captures/jobs/`](captures/jobs/): asynchronous submission, polling,
  results, and dismissal sequences.
- [`diagnostics/`](diagnostics/): error summary, process-selection records, and
  direct OTB checks that are not normal HTTP exchanges.

See the [evidence README](../README.md) for the request and response formats.

## Run a request

```bash
python3 scripts/run_evidence_request.py hellojs_string --print-curl
python3 scripts/run_evidence_request.py hellojs_string
```

To capture the response in the standard format:

```bash
python3 scripts/run_evidence_request.py hellojs_string --save-response
```

To test the same request at another URL:

```bash
python3 scripts/run_evidence_request.py hellojs_string \
  --base-url https://example.org/ogc-api
```

## Copy fixtures into the container

Some older GDAL and OGR processes expect a filename inside the ZOO container:

```bash
python3 scripts/stage_zoo_fixtures.py --dry-run
python3 scripts/stage_zoo_fixtures.py
```

This is only local evidence infrastructure. A browser client does not copy
fixtures into a processing server.

## Notable SAGA behaviour

The 18 main SAGA requests originally returned:

- 11 usable results with HTTP 200;
- two HTTP 200 responses without the requested output;
- one HTTP 200 response linking to a file that did not exist;
- four HTTP 500 process crashes or aborts.

Three raster processes worked with one input but returned `SIGSEGV` when given
repeated input through a field that the description marked as repeatable.

These captures show that following a process description does not guarantee
that the provider can execute the request, and that HTTP 200 does not guarantee
that the requested output is present or usable.

## Notable OTB behaviour

Five OTB descriptions loaded successfully, but the corresponding executions
returned HTTP 500 with `No OTB Application found.` Direct command-line checks
succeeded with the same inputs. The client therefore should not present this
particular failure as invalid user data.

`OTB.ReadImageInfo` failed earlier: its description endpoint returned an HTML
HTTP 500 response after the ZOO loader crashed. A client should mark that
process description as unavailable without treating the complete process list
as unusable.

The other OTB descriptions remain useful input-schema examples. They include
repeated image inputs, dotted input IDs, conditional fields, and an ID that
appears in both the input and output lists.
