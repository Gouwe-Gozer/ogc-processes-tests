# Client-observable process families

## Purpose

This document groups the 50 selected processes by behaviour that matters
to an OGC API - Processes client and its UI. The goal is a smaller regression
suite that still exercises the relevant request controls, complex-data
transport, result shapes, job lifecycle, error messages, and defective server
behaviour.

These are not algorithm or provider-library families. For example,
`Intersection`, `Union`, and `Difference` are different geospatial operations,
but their process descriptions lead a generic client through the same flow:
two complex geometry inputs, synchronous execution, and one complex geometry
output. Conversely, two processes from the same SAGA library belong to
different client families when one returns a raster reference and another
returns several inline vectors.

The grouping is based on the captured profile
`zoo-ubuntu18-gdal3-saga7-otb7`. It should be reviewed when a description or
observed response changes.

## What makes processes equivalent for the client

Processes can share a representative when they exercise the same combination
of:

- execution lifecycle: synchronous response or asynchronous job;
- input controls: primitive, object, complex value/reference, and cardinality;
- complex-data delivery: inline UTF-8, inline base64, or `href`;
- output shape: literal, single complex, repeated complex, or multiple named
  outputs;
- output transmission: inline value or reference;
- response outcome: usable success, terminal job failure, HTTP problem,
  incomplete success, or unusable reference.

The operation's mathematical meaning is not by itself a reason to keep another
client test. Direction-sensitive geometry operations can still deserve domain
tests, but those are process correctness tests rather than client/UI coverage.

## Primary behaviour families

Each of the 50 process IDs appears once in this table. Important error and
response variants are listed separately below because they cut across these
primary request/response families.

| Family | Client-observable contract | Processes | Representatives for client testing |
|---|---|---|---|
| 1. Minimal literal document | Primitive input and one inline literal output in a synchronous document | `hellojs` | `hellojs` |
| 2. Mixed structured echo | Optional literal, complex JSON, and bounding-box inputs with matching heterogeneous outputs | `EchoProcess` | `EchoProcess` |
| 3. Asynchronous job lifecycle | Integer input, HTTP 201 submission, job location, polling, and terminal state | `longProcess`, `demo` | Both: one succeeds and one fails |
| 4. Geometry to scalar | One or two referenced geometries producing a number or Boolean | `GetArea`, `Distance`, `Contains`, `IsValid` | `Distance` for number and two inputs; `Contains` for Boolean |
| 5. Unary vector transformation | One vector input, sometimes literals/options, producing one vector result | `Boundary`, `Centroid`, `ConvexHull`, `Delaunay`, `Buffer`, `Simplify`, `SAGA.shapes_polygons.5`, `SAGA.shapes_points.16` | `Buffer` for the usable path; retain fault variants for missing output and provider abort |
| 6. Binary vector transformation | Two vector inputs producing one vector result | `Intersection`, `Union`, `Difference`, `SymDifference`, `SAGA.shapes_polygons.14` | `Intersection`; a SAGA abort adds no new message beyond the retained `SIGABRT` representative |
| 7. Server-side filename workflow | Literal path/option inputs; provider reads and writes inside its own filesystem; result is a path-like literal | `Gdal_Translate`, `Gdal_Warp`, `Gdal_Dem`, `Gdal_Contour`, `Gdal_Grid`, `Ogr2Ogr` | `Gdal_Translate` success, `Gdal_Grid` error without detail, and `Ogr2Ogr` malformed result URL |
| 8. Server filename plus remote complex input | Server-side raster filename combined with referenced geometry; inline structured result | `GdalExtractProfile` | `GdalExtractProfile` |
| 9. Raster to raster | Raster complex input, raster options and enums, and raster output by reference; some inputs/outputs are repeatable | `SAGA.grid_tools.0`, `SAGA.grid_tools.3`, `SAGA.grid_tools.27`, `SAGA.grid_calculus.1`, `SAGA.grid_filter.1`, `OTB.BandMath` | `SAGA.grid_tools.0` success plus repeated-input failure; `SAGA.grid_tools.27` for a missing repeated output; `OTB.BandMath` for overlapping input/output ID and unavailable runtime |
| 10. Vector or point cloud to raster | Vector, support raster, or binary LAS input and one or more raster outputs | `SAGA.grid_gridding.1`, `SAGA.pointcloud_tools.4`, `OTB.Rasterization` | `SAGA.pointcloud_tools.4` for inline base64 binary input; `OTB.Rasterization` adds conditional inputs and the OTB runtime error |
| 11. Mixed or multiple complex outputs | Raster/vector combinations, conditional outputs, and two to five named complex outputs | `SAGA.shapes_grid.5`, `SAGA.shapes_grid.0`, `SAGA.shapes_lines.3`, `SAGA.tin_tools.2`, `SAGA.tin_tools.3`, `OTB.Segmentation` | `SAGA.shapes_grid.5` for successful multiple outputs; the `OTB.Segmentation` description is retained for dotted conditional fields |
| 12. Tabular or XML result | Literal, CSV, or raster inputs producing CSV, table, or XML output by value or reference | `SAGA.table_tools.0`, `SAGA.table_tools.3`, `SAGA.statistics_grid.5`, `OTB.ComputeImagesStatistics` | `SAGA.table_tools.3` usable CSV, `SAGA.table_tools.0` invalid reference, and the OTB description for repeated raster input to XML |
| 13. Immediate provider problem | Synchronous literal request deliberately returning an OGC problem | `failR` | `failR` |
| 14. Raster to literal | Raster complex input plus coordinates and enum producing an inline literal | `OTB.PixelValue` | `OTB.PixelValue`; execution also represents the unavailable OTB runtime error |
| 15. Individual description failure | Process appears in the collection but GET of its description fails before execution can be constructed | `OTB.ReadImageInfo` | `OTB.ReadImageInfo` |

## Recommended compact suite

The following suite contains 22 process IDs and 23 cases, compared with 50
process IDs and 53 current cases. The second `SAGA.grid_tools.0` case is an
intentional negative variant of the same process.

| Process | Case | Coverage retained |
|---|---|---|
| `hellojs` | `hellojs_string` | Minimal synchronous literal request/result |
| `EchoProcess` | `echo_all_input_kinds` | Optional inputs, JSON object, bounding box, and heterogeneous outputs |
| `longProcess` | `long_process_async` | Accepted async job and successful terminal state |
| `demo` | `demo_async_expected_failure` | Accepted async job followed by terminal failure and job message |
| `Distance` | `distance_polygons` | Two complex references and numeric output |
| `Contains` | `contains_polygon_point` | Two complex references and Boolean output |
| `Buffer` | `buffer_polygon` | Complex GeoJSON reference plus numeric literal to inline vector |
| `Intersection` | `intersection_polygons` | Two vector inputs to one vector output |
| `Gdal_Translate` | `gdal_translate_raster` | Server-side filename input/output and staged-fixture warning |
| `Gdal_Grid` | `gdal_grid_points` | Description-conformant HTTP 500 with no useful provider message |
| `Ogr2Ogr` | `ogr2ogr_vector` | HTTP 200 containing a malformed URL-like result |
| `GdalExtractProfile` | `gdal_extract_profile_line` | Server filename plus remote geometry reference to structured JSON |
| `SAGA.grid_tools.0` | `saga_resample_rasters` | Referenced AAIGrid, raster controls, and TIFF output reference |
| `SAGA.grid_tools.0` | `saga_resample_rasters_repeated_input_expected_error` | Advertised repeated raster input causing `SIGSEGV` |
| `SAGA.grid_tools.27` | `saga_tile_raster` | HTTP 200 with a missing requested repeated output |
| `SAGA.shapes_grid.5` | `saga_contours_raster` | Raster input to two named inline GeoJSON outputs |
| `SAGA.shapes_points.16` | `saga_thiessen_points` | Description-conformant vector request causing `SIGABRT` |
| `SAGA.table_tools.0` | `saga_create_table` | HTTP 200 with an unusable, incorrectly typed reference |
| `SAGA.table_tools.3` | `saga_join_tables` | Two inline UTF-8 CSV inputs and inline CSV output |
| `SAGA.pointcloud_tools.4` | `saga_pointcloud_to_grid` | Inline base64 LAS and a provider crash |
| `failR` | `fail_r_expected_error` | Immediate provider problem with distinct error detail |
| `OTB.BandMath` | `otb_band_math` | Repeated images, overlapping input/output ID, and unavailable-runtime problem |
| `OTB.ReadImageInfo` | `otb_read_image_info_description_expected_error` | Individual description returns non-JSON HTML 500 after loader crash |

This compact suite preserves all seven distinct captured error messages:

- asynchronous `Error executing the service`;
- `Failed running from R world!`;
- `No message provided`;
- provider `SIGSEGV`;
- provider `SIGABRT`;
- `No OTB Application found.`;
- generic Apache internal-server-error HTML from a description endpoint.

It also preserves three failures that do not arrive as an ordinary error
problem: a malformed URL-like output, a missing output in an HTTP-200 body, and
an output reference whose advertised target does not exist.

## Why the remaining processes can normally be omitted

- The other GEOS operations change geometry semantics, but not the client's
  input wrapper, reference handling, execution envelope, or output parsing.
- `Gdal_Warp`, `Gdal_Dem`, and `Gdal_Contour` add provider options and different
  algorithms, but the server-filename behaviour is already represented.
- The successful SAGA mosaic, calculator, and filter cases repeat the same
  raster-reference-to-raster-reference client flow as resampling.
- SAGA line and TIN conversions increase the number of vector outputs, but the
  client already has to support arbitrary named outputs after the two-output
  contour case. A separate upper-bound UI test can synthesize five outputs if
  layout stress is important.
- SAGA zonal statistics composes raster input behaviour with CSV result
  behaviour that is already covered independently.

The full suite remains valuable for provider regression and process correctness.
The compact suite is specifically for client protocol and UI coverage.

## How OTB coverage is reduced

The six OTB cases add description/UI shapes not represented as strongly by the
original 44 processes:

- repeated image lists plus an expression;
- the same ID in separate input and output namespaces;
- dotted conditional parameter IDs;
- conditionally relevant fields advertised as simultaneously required;
- raster/vector conditional outputs;
- a process-description endpoint returning HTML 500 instead of JSON.

All five executable requests currently return the same `InternalError` because
ZOO's OTB application registry is empty. `OTB.BandMath` is the compact live
representative for that error. All five descriptions remain required contract
fixtures for form-generation and raw-JSON-fallback tests, even though routine
live execution need not repeat the identical error five times.
`OTB.ReadImageInfo` remains a separate required GET case because discovery
fails before execution.

## Negative-input and faulty-response families

Negative tests should be organized by what the client can safely know. A
request passing client validation only means it matches the advertised
description; it does not guarantee provider success.

### 1. Description-detectable invalid input

These should normally be caught before submission when the relevant schema is
understood:

| Fault | Suggested representative | Expected client safeguard |
|---|---|---|
| Missing required input | omit `S` from `hellojs` | Identify the missing input by exact ID |
| Wrong primitive type | send a string for `longProcess.sid` or `BufferDistance` | Report expected and received JSON types without coercing silently |
| Invalid enum member | use an unknown advertised-option value in a SAGA raster case | List the advertised values and preserve raw JSON editing as the escape hatch |
| Invalid bounding-box length | give `EchoProcess.c.bbox` neither four nor six numbers | Report the array constraint |
| Too many values | exceed an advertised `maxOccurs` or `maxItems` | Report cardinality before submission |
| Unknown input/output ID | add an identifier absent from the current description | Warn that the field is not described; do not silently remove it in raw mode |
| Unsupported transmission or execution mode | request a mode not advertised by the process | Block the generated request while retaining raw-mode access where promised |

### 2. Description-conformant input that the provider rejects or crashes on

These cases are particularly important because client-side schema validation
must allow them:

| Request shape | Observed behaviour | Safe client conclusion |
|---|---|---|
| Two rasters in the repeated `INPUT` of `SAGA.grid_tools.0` | HTTP 500, `SIGSEGV` | The provider crashed on a description-conformant request; no specific input can be blamed from the message alone |
| Advertised-only inputs for `Gdal_Grid` | HTTP 500, `No message provided` | The server supplied no actionable diagnostic; the client must not invent its unadvertised layer/band parameters |
| Point GML supplied to the broadly described `Distance` geometry input | Provider rejects it, while polygons work | Media type and generic geometry wording do not prove that every geometry subtype is implemented |
| Advertised `SAGA.grid_gridding.1` point/grid request | HTTP 500, `SIGSEGV` | Provider failure after a valid envelope; optional controls do not explain the failure |
| Advertised SAGA polygon intersection or Thiessen request | HTTP 500, `SIGABRT` | Provider abort; preserve the exact request and raw problem |
| Valid base64 LAS wrapper for `SAGA.pointcloud_tools.4` | HTTP 500, `SIGSEGV` | Successful base64/schema validation does not prove that the provider imported the dataset |
| `Gdal_Dem` hillshade using only advertised inputs | Implementation needs an unadvertised `z` value | Offer the verified advertised slope path; do not fabricate a hidden field |

The compact suite retains one case for every distinct captured error message
and keeps both a repeated-raster and binary-LAS `SIGSEGV` occurrence. That
guards against overfitting the warning to one input type.

### 3. Valid wrapper with unusable referenced content

These requests may be structurally valid but fail outside what description
validation can establish:

- an unreachable `href` from the process server's network context;
- a response served with the requested media type but invalid content;
- syntactically valid base64 that decodes to a corrupt raster or LAS file;
- a browser-local path supplied to a server-side filename input;
- a referenced geometry whose media type is accepted but whose geometry subtype
  is not supported by the provider.

The client can validate URL and wrapper syntax. It cannot promise that the
remote server can fetch or semantically import the content. The resulting
problem response should retain status, headers, final URL, parsed problem
fields, and raw body.

### 4. Faulty or incomplete success response

HTTP success must be checked independently from result completeness:

| Observed response | Representative | Useful warning |
|---|---|---|
| HTTP 200 with `{}` and no requested output | `SAGA.grid_tools.27`; also observed for `SAGA.shapes_polygons.5` | The process returned success status but omitted the requested output ID |
| URL-like literal is malformed | `Ogr2Ogr` | Preserve and display the literal; do not blindly treat every string as a fetchable URL |
| Reference is syntactically present but cannot be retrieved | `SAGA.table_tools.0` | Report reference retrieval failure separately from execution status |
| Output ID is unknown to the description | synthetic response test | Preserve the output for forward compatibility and mark it as undescribed |
| Declared media type disagrees with retrieved content | synthetic response or tested service | Retain both declared and observed information; do not silently reinterpret data |

### 5. Asynchronous failure after accepted submission

`demo` returns HTTP 201 when the job is accepted and later reaches terminal
state `failed`. The client must not present the submission response as process
success. It should show the terminal job message and keep submission and job
evidence distinct.

## Evidence required for every negative case

Every negative case should preserve:

1. the exact process description used for validation;
2. the exact submitted request body and relevant headers;
3. HTTP status, response headers, final URL, and raw response body;
4. asynchronous job status and message where applicable;
5. whether the request violates an advertised constraint or conforms to it;
6. the narrow warning the client may safely show;
7. what the response does **not** justify inferring.

The captured messages and their safe interpretations are indexed in
[`evidence/zoo/ERROR_CATALOG.md`](evidence/zoo/ERROR_CATALOG.md). The SAGA
outcome matrix is in
[`evidence/zoo/SAGA_EXECUTION_OBSERVATIONS.md`](evidence/zoo/SAGA_EXECUTION_OBSERVATIONS.md).

## When to run which suite

- Run the compact suite for routine protocol-core and UI regression.
- Run synthetic description/request/response tests for constraints that do not
  need a live geospatial algorithm, such as wrong types, unknown outputs, and
  media-type mismatches.
- Run all 50 processes when validating a ZOO image, provider upgrade, fixture
  change, or process-specific correctness.
- Promote another process into the compact suite only when it adds a new
  client-observable input, output, lifecycle, or failure behaviour.
