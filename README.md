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
python scripts/run_case.py cases/hellojs_string \
  --base-url http://localhost/ogc-api
```

If the host does not provide a `python` alias, use `python3` instead.

Print the equivalent curl command without sending it:

```bash
python scripts/run_case.py cases/hellojs_string \
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

## Cases

- `hellojs_string` is a basic synchronous string-input smoke test.
- `rvoronoi_five_points` sends the five Alkmaar points to `RVoronoi`. The
  captured ZOO process description advertises only GML 3.1 XML for
  `InputPoints`, so its request embeds GML derived from the GeoJSON fixture.
  This deliberate duplication makes the exact interoperable payload visible
  while keeping the small GeoJSON fixture reusable by clients. On the local
  server inspected on 2026-08-24, ZOO accepted the execution request but the R
  service failed because `readOGR` was unavailable; the observed error is
  retained under `evidence/zoo/` and the case still expects a successful 200
  response.

## Fixture conventions

Spatial fixtures:

- are located in the Netherlands, currently around Alkmaar;
- cover a deliberately small geographic extent;
- use WGS 84 longitude/latitude (OGC CRS84 / RFC 7946 coordinate order);
- follow GeoJSON RFC 7946 and do not contain an obsolete `crs` member;
- are deterministic, small, readable, and committed to Git.

Raster tests are deferred until a real raster process is added; see
`fixtures/raster/README.md`.

## Evidence and Postman

`evidence/zoo/` contains machine-readable process descriptions fetched from
the local ZOO service. They provide traceability from advertised process
metadata to request and observed behaviour.

Postman is optional. See `postman/README.md` and the starter collection for a
convenient interface over the canonical files.
