# Compact process-execution client suite

This suite applies the client-testcase format to the 22 process IDs and 23
cases selected in
[`../../PROCESS_BEHAVIOUR_FAMILIES.md`](../../PROCESS_BEHAVIOUR_FAMILIES.md).
It tests client-observable request and response shapes, not the mathematical
correctness of every provider algorithm.

The two asynchronous representatives are already covered by
[`../async-jobs/`](../async-jobs/). This directory contains the other 21
execution or description cases plus three description-detectable invalid-input
variants.

## Layout by client handling

```text
process-execution/
├── usable-results/          HTTP 200 with useful literal or complex outputs
├── server-file-paths/       server-side filename inputs and result strings
├── incomplete-results/     HTTP 200 but missing or unusable result data
├── provider-problems/       JSON HTTP problems from conformant requests
├── description-problems/    a process description that returns non-JSON 500
└── validation-errors/       input the description lets the client reject
```

These folders describe what the client has to do. They are deliberately not
grouped by GDAL, GEOS, SAGA, or OTB, because the generic client should not need
provider-specific execution code.

## Error-message policy

Useful provider detail can be presented safely and mostly unchanged:

```text
Request failed — server message: “<server message>”
```

The distinct `SIGSEGV`, `SIGABRT`, R, GDAL, and OTB messages are retained as
profile evidence, but they do not require a translation catalogue or separate
UI flows. The useful generic distinction is between:

- an HTTP problem with usable detail;
- an HTTP problem with missing or poor detail;
- a non-JSON HTTP error;
- HTTP success containing a usable result;
- HTTP success containing a missing or unusable result.

The client must escape returned text, retain status and raw body, and avoid
assigning an input cause unless the response actually identifies one.

## Selected process coverage

| Process | Canonical case | Client value |
|---|---|---|
| `hellojs` | `hellojs_string` | Minimal string input and string result |
| `EchoProcess` | `echo_all_input_kinds` | Optional literal, wrapped JSON, bounding box, and three heterogeneous outputs |
| `longProcess` | `long_process_async` | Successful async lifecycle; covered under `async-jobs` |
| `demo` | `demo_async_expected_failure` | Failed terminal job with pass-through message; covered under `async-jobs` |
| `Distance` | `distance_polygons` | Two referenced GML inputs and numeric zero result |
| `Contains` | `contains_polygon_point` | Ordered referenced geometry inputs and Boolean result |
| `Buffer` | `buffer_polygon` | Referenced GeoJSON plus numeric literal to wrapped GeoJSON value |
| `Intersection` | `intersection_polygons` | Two references to one wrapped vector output |
| `Gdal_Translate` | `gdal_translate_raster` | Server-side filename inputs and a server-local result path |
| `Gdal_Grid` | `gdal_grid_points` | Description-conformant HTTP 500 with no actionable detail |
| `Ogr2Ogr` | `ogr2ogr_vector` | HTTP 200 with a malformed URL-like literal result |
| `GdalExtractProfile` | `gdal_extract_profile_line` | Server filename plus remote geometry reference to structured coordinates |
| `SAGA.grid_tools.0` | `saga_resample_rasters` | Referenced raster input and TIFF output by reference |
| `SAGA.grid_tools.0` | `saga_resample_rasters_repeated_input_expected_error` | Advertised repeated references/inline base64 followed by provider crash |
| `SAGA.grid_tools.27` | `saga_tile_raster` | Requested repeated output omitted from an HTTP-200 body |
| `SAGA.shapes_grid.5` | `saga_contours_raster` | One raster to two named inline GeoJSON outputs |
| `SAGA.shapes_points.16` | `saga_thiessen_points` | Description-conformant referenced vector followed by provider abort |
| `SAGA.table_tools.0` | `saga_create_table` | Syntactically present but incorrectly typed and unreachable reference |
| `SAGA.table_tools.3` | `saga_join_tables` | Two inline UTF-8 CSV inputs and inline CSV result |
| `SAGA.pointcloud_tools.4` | `saga_pointcloud_to_grid` | Inline base64 LAS with multiple requested raster outputs and provider crash |
| `failR` | `fail_r_expected_error` | Immediate provider problem with useful detail |
| `OTB.BandMath` | `otb_band_math` | Repeated base64 images and the same `out` ID in separate input/output namespaces |
| `OTB.ReadImageInfo` | `otb_read_image_info_description_expected_error` | One broken process description must not poison collection discovery |

[`suite.json`](suite.json) is the machine-readable index. It records the two
cases implemented by the async suite rather than duplicating their POST and job
fixtures here.

## Additional validation cases

The compact live cases include requests that conform to their descriptions but
still fail in a provider. Two additional cases test what the client can reject
before transport:

| Case | Description rule | Observed server behaviour if sent | Preferred client behaviour |
|---|---|---|---|
| `missing_required_hellojs` | Required `inputs.S` is absent | HTTP 400 `MissingParameterValue` | Identify the missing exact ID and normally do not send |
| `invalid_bbox_echo` | `bbox` must contain four or six numbers | Server nevertheless echoes five numbers with HTTP 200 | Report the array constraint and do not treat server acceptance as schema validation |
| `invalid_enum_saga_resample` | `TARGET_DEFINITION` has two advertised values | Server nevertheless returns a TIFF reference with HTTP 200 | List the advertised values and preserve the invalid raw value without silently defaulting |

Wrong primitive type is already covered by
[`../async-jobs/request-errors/description-invalid-input/`](../async-jobs/request-errors/description-invalid-input/).
Together these cases cover missing required values, wrong types, nested array
cardinality, and enums without repeating each fault for every process.

## Deliberate reductions

- Healthy process-description GETs are not repeated as a step before every
  POST. Their captured bodies under `evidence/zoo/` are the contract fixtures
  used by these tests; landing-page discovery and link traversal can be tested
  once in a later discovery suite. The broken `OTB.ReadImageInfo` GET remains
  here because it changes client behaviour before execution.
- Every selected process does not receive its own missing-input, wrong-type,
  enum, cardinality, and unknown-field variant. The three validation cases here
  plus the async wrong-type case cover the important validation mechanisms
  without a large cross-product.
- A successful binary download is not repeated for every result reference.
  The protocol core must expose the href and media type; rendering and download
  persistence remain outside it. One failed reference GET is retained because
  it proves that execution success and reference retrieval are separate.
- Exact provider error wording is evidence, not a separate UI behaviour. The
  structured-useful, structured-unhelpful, and non-JSON families are enough for
  generic presentation.

## Client assertions versus provider assertions

Client tests should assert the execution envelope, HTTP classification, output
IDs, wrappers, media-type metadata, and whether a referenced result is usable.
They should not assert every coordinate, raster value, or provider-specific
message byte-for-byte.

In particular:

- HTTP 200 does not guarantee that requested output IDs are present;
- a string that resembles a URL is still a literal unless its result wrapper
  identifies it as a reference;
- a reference wrapper can be syntactically valid while its target is missing;
- server-local filenames are not browser-download URLs;
- a description-conformant request may still be rejected or crash a provider;
- unsupported or broken descriptions remain isolated and available as raw
  evidence rather than breaking the rest of process discovery.

The response bodies checked in here are representative profile observations.
Dynamic filenames and identifiers can vary between executions, so live tests
should compare structure and usability rather than exact strings.

The current responses were captured against profile
`zoo-ubuntu18-gdal3-saga7-otb7` on 2026-08-25. Another service or upgraded
provider stack can legitimately return different algorithm values, messages,
references, or failures while exercising the same client behaviour family.
