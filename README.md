# OGC API Processes tests

This repository contains small, reusable OGC API Processes interoperability
fixtures and test cases. It intentionally does not depend on Postman or a
particular client implementation.

## Canonical artefacts

The source of truth is ordinary, inspectable text:

```text
case.json
request.json
fixtures/
```

curl, Postman, `scripts/run_case.py`, and a future Topic 3 client are consumers
of those artefacts. Process descriptions captured under `evidence/` record why
a request has its particular shape.

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

All 44 core selected processes now have an executable case directory. Three
SAGA raster processes additionally have expected-error cases that preserve the
provider's failure on advertised repeated inputs, for 47 POST cases in total.
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

Refresh selected descriptions with the standard-library capture helper:

```bash
python3 scripts/fetch_process_descriptions.py hellojs EchoProcess \
  --base-url http://localhost/ogc-api
```

Postman is optional. See `postman/README.md` and the starter collection for a
convenient interface over the canonical files.
