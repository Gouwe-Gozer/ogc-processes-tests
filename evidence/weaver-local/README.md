# Local Weaver server

This folder contains evidence from Weaver 6.15.0 in `HYBRID` mode at
`http://localhost:4001`. The captures were made on 31 August 2026.

The server exposes six built-in processes. Discovery and all six process
descriptions returned complete JSON responses with HTTP 200.

## Contents

- [`captures/discovery/`](captures/discovery/): landing page, conformance
  declaration, and process list;
- [`captures/descriptions/`](captures/descriptions/): all six descriptions,
  plus JSON and HTML unknown-process errors;
- [`captures/executions/`](captures/executions/): a successful rich synchronous
  execution, validation errors, and two failures caused by defects in built-in
  CWL definitions;
- [`captures/jobs/`](captures/jobs/): a successful async workflow, a failed
  async workflow, job listing, and job-related errors;
- [`diagnostics/cors/`](diagnostics/cors/): the browser execution preflight.

## Execution findings

`EchoProcess` completed successfully in both sync and async mode. Its request
and results cover primitive values, arrays, structured JSON, geometries, a
bounding box, an image, and a feature collection.

Two built-ins failed despite valid requests:

- `file2string_array` uses a Python executable path that is absent from the
  published `latest-worker` image;
- `file_index_selector` produces multiple output matches for an output its CWL
  declares as a single file.

These are process-package defects, not missing worker services and not invalid
end-user input. The captured logs contain the exact messages.

The successful Echo job also exposed output-access problems. Its referenced
JSON object was readable, although the file proxy omitted `Content-Type`.
Referenced geometry, feature-collection, and TIFF URLs returned HTTP 403. The
job itself was still reported as `successful`, so a client must handle a result
link failing independently of the job.

## Run a capture

With Weaver available at `http://localhost:4001`:

```bash
python3 scripts/run_evidence_request.py missing-required-input \
  --server weaver-local --print-curl
python3 scripts/run_evidence_request.py missing-required-input \
  --server weaver-local
```

Refresh selected process descriptions with:

```bash
python3 scripts/capture_process_descriptions.py \
  --server weaver-local EchoProcess file2string_array
```

## Browser access

The execution preflight returned HTTP 405 without CORS permission headers. A
browser cannot call this deployment directly from another origin. The client
would need the promised relay transport.
