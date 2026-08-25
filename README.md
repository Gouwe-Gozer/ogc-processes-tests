# OGC API Processes tests

This repository contains small, reusable OGC API Processes interoperability
fixtures and test cases. It intentionally does not depend on Postman or a
particular client implementation.

## Canonical artefacts

The source of truth is ordinary, inspectable text. Provider/profile execution
cases use:

```text
case.json
request.json
fixtures/
```

curl, Postman, `scripts/run_case.py`, and a future Topic 3 client are consumers
of those artefacts. Process descriptions captured under `evidence/` record why
a request has its particular shape.

Client protocol behaviour is kept separately under
[`client-testcases/`](client-testcases/). Those ordered HTTP exchanges cover
successful and incorrect requests, async polling, results, dismissal, HTTP
problems, and malformed responses. Every step states how the client should
classify the returned body and what misleading behaviour it must avoid.

## Quick start

Execute the literal-input smoke test against a local ZOO-Project instance:

```bash
python3 scripts/run_case.py cases/hellojs_string \
  --base-url http://localhost/ogc-api
```

If the host does not provide a `python` alias, use `python3` instead.

Print the equivalent curl command without sending it:

```bash
python3 scripts/run_case.py cases/hellojs_string \
  --base-url http://localhost/ogc-api \
  --print-curl
```

Each case directory contains a small `case.json` plus the exact HTTP body in
`request.json`. The runner derives this endpoint from `process_id`:

```text
POST {baseUrl}/processes/{process_id}/execution
```

It exits successfully only when the response status equals
`expected.http_status`.

To preserve a raw response body as execution evidence while running a case:

```bash
python3 scripts/run_case.py cases/hellojs_string \
  --base-url http://localhost/ogc-api \
  --response-output /tmp/hellojs.execution.json
```

## Cases

All 50 selected entries now have a case. The original 44 processes include
three additional SAGA expected-error variants for advertised repeated inputs.
The six required OTB entries add five POST execution cases and one GET
description case. The generated collection therefore contains 52 POST cases
plus one explicit description case.
Filename-based GDAL/OGR cases require fixtures to be staged in the local ZOO
profile first. See `cases/README.md` for the inventory and observed outcomes.

The runner exits with code `3` when asked to execute a future pending case. It
adds `Prefer: respond-async` automatically for cases whose `execution_mode` is
`async`.

## Fixture conventions

Spatial fixtures:

- are located in the Netherlands, currently around Alkmaar;
- cover a deliberately small geographic extent;
- use WGS 84 longitude/latitude (OGC CRS84 / RFC 7946 coordinate order);
- follow GeoJSON RFC 7946 and do not contain an obsolete `crs` member;
- are deterministic, small, readable, and committed to Git.

A small text DEM is available for the selected raster processes. Stage local
fixtures with `python3 scripts/stage_zoo_fixtures.py` before running the
filename-based GDAL/OGR cases. See `fixtures/raster/README.md`.

## Evidence and Postman

`evidence/zoo/` contains machine-readable process descriptions fetched from
the local ZOO service. They provide traceability from advertised process
metadata to request and observed behaviour.

See [`CLIENT_IMPLEMENTATION_LESSONS.md`](CLIENT_IMPLEMENTATION_LESSONS.md) for
the client-facing lessons from comparing those descriptions with their exact
requests and observed execution behaviour. The SAGA execution matrix and
provider failures are indexed under `evidence/zoo/`.

The OTB descriptions, expected execution errors, direct fixture
validation, and `ReadImageInfo` description failure are summarized in
[`evidence/zoo/OTB_EXECUTION_OBSERVATIONS.md`](evidence/zoo/OTB_EXECUTION_OBSERVATIONS.md).

The initial client protocol suite is documented in
[`client-testcases/async-jobs/README.md`](client-testcases/async-jobs/README.md).
It covers successful, failed, and dismissed jobs plus request and response
faults without multiplying every async state across all process families.

[`PROCESS_BEHAVIOUR_FAMILIES.md`](PROCESS_BEHAVIOUR_FAMILIES.md) groups all 50
selected process IDs by client-observable behaviour and proposes a compact
regression suite that retains input/output, lifecycle, error-message, and
malformed-result coverage.

Refresh selected descriptions with the standard-library capture helper:

```bash
python3 scripts/fetch_process_descriptions.py hellojs EchoProcess \
  --base-url http://localhost/ogc-api
```

Postman is optional. See `postman/README.md` and the starter collection for a
convenient interface over the canonical files.
