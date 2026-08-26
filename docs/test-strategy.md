# Test strategy

## Probes and client testcases

The repository contains two kinds of tests:

- `deployments/<name>/probes/` contains requests that can be sent to a specific
  server. Use these to reproduce and capture server behavior.
- `testcases/` contains request and response examples with the behavior we
  expect from the client.

For example, a ZOO probe may record that a SAGA process crashes. The related
client testcase checks that the client shows an HTTP error and keeps the server
message. The client does not need SAGA-specific code.

`testcases/suite.json` lists all 39 client testcases:

- 25 can be run against a live server;
- 5 are manual because timing or client-side validation matters;
- 9 use recorded responses for errors that are difficult to reproduce safely.

After adding or moving a testcase, update the list and check all files:

```bash
python3 scripts/validate_repository.py --write-suite
```

## Coverage of the Topic 3 plan

This repository supplies test data and evidence for the OGC API Processes
client described in the Topic 3 plan of approach. It does not implement the
client or prove that a client feature works by itself. A feature is verified
only after a test calls the actual client and checks its behavior against these
examples.

The current coverage is:

| Topic 3 commitment | Coverage in this repository |
|---|---|
| Process discovery and descriptions | Partial: process descriptions are captured, but landing-page, conformance, and process-list testcases are still missing |
| Generated forms | Partial: required inputs, enums, bounding boxes, and primitive types are represented, but the generated UI is not tested here |
| Raw JSON fallback | Documented, but not yet tested through a client |
| Synchronous execution | Strong coverage of successful, failed, raw, and document responses |
| Async submission, polling, results, and dismiss | Strong coverage of successful, failed, incomplete, and dismissed jobs |
| Result rendering | Partial: useful result samples exist, but the choice between map, inline view, JSON view, and download is not tested |
| CORS and exposed `Location` | Missing |
| Subscriber callbacks and polling reconciliation | Missing |
| OGC API Processes v1 and v2 selection | Missing |
| Different server implementations | Limited: most live testcases use the local ZOO deployment; two recorded pygeoapi examples cover additional response shapes |
| Interoperability matrix | The repository can provide evidence for it, but the matrix has not been created yet |

Provider-specific failures remain useful as evidence, but they should not
create provider-specific client behavior. For example, separate OTB, SAGA, and
GDAL failures can all verify the same client rule: preserve the HTTP response,
show the server message safely, and keep the rest of the client usable.

## Testcase folders

| Folder | What is tested |
|---|---|
| `descriptions` | One process description fails without breaking the full process list |
| `errors` | The server returns an HTTP error |
| `execution-sync` | A synchronous request returns usable results |
| `jobs` | Submit, poll, fetch results, and dismiss asynchronous jobs |
| `malformed-responses` | The server returns incomplete or invalid data |
| `validation` | The client finds bad input before sending it |

Landing-page and conformance tests have not been added yet. When they are
added, put them in `testcases/discovery/`.

## Choosing a smaller process set

The local ZOO server has many processes that look different but require the
same client behavior. For example, `Intersection`, `Union`, and `Difference`
all send two geometries and receive one geometry. One successful example is
usually enough to test that request and result shape.

Keep another process when it adds a different input, result, job flow, or error.

| Request or result shape | Processes considered | Main examples kept for client tests |
|---|---|---|
| Simple text input and output | `hellojs` | `hellojs` |
| Mixed text, JSON, and bounding box | `EchoProcess` | `EchoProcess` |
| Asynchronous job | `longProcess`, `demo` | both, because one succeeds and one fails |
| Geometry to number or Boolean | `GetArea`, `Distance`, `Contains`, `IsValid` | `Distance`, `Contains` |
| One geometry to one geometry | GEOS and SAGA single-input tools | `Buffer` plus a SAGA error |
| Two geometries to one geometry | GEOS and SAGA two-input tools | `Intersection` |
| Filenames inside the server | GDAL/OGR wrappers | `Gdal_Translate`, `Gdal_Grid`, `Ogr2Ogr` |
| Server raster plus remote geometry | `GdalExtractProfile` | `GdalExtractProfile` |
| Raster to raster | SAGA grid tools and `OTB.BandMath` | SAGA success, missing result, repeated-input crash, and OTB error |
| Vector or LAS to raster | SAGA gridding/point-cloud and OTB rasterization | LAS request and OTB conditional description |
| Several named vector outputs | SAGA shape/TIN tools and OTB segmentation | SAGA contour outputs and OTB description |
| CSV, table, or XML output | SAGA table/statistics and OTB statistics | usable CSV, bad output link, and OTB description |
| Immediate server error | `failR` | `failR` |
| Raster to simple value | `OTB.PixelValue` | OTB description and shared OTB runtime error |
| Broken process description | `OTB.ReadImageInfo` | `OTB.ReadImageInfo` |

The smaller ZOO client set uses these 22 process IDs:

```text
hellojs, EchoProcess, longProcess, demo, Distance, Contains, Buffer,
Intersection, Gdal_Translate, Gdal_Grid, Ogr2Ogr, GdalExtractProfile,
SAGA.grid_tools.0, SAGA.grid_tools.27, SAGA.shapes_grid.5,
SAGA.shapes_points.16, SAGA.table_tools.0, SAGA.table_tools.3,
SAGA.pointcloud_tools.4, failR, OTB.BandMath, OTB.ReadImageInfo
```

The full set of 53 probes is still useful when checking the ZOO container or a
new provider version. The two pygeoapi examples add a deeply nested JSON result
and raw-versus-document responses. They do not repeat the full ZOO set.

## Bad input and bad response cases

The test suite needs examples from each of these groups:

1. **The client can find the input error.** Examples: missing required input,
   wrong type, invalid allowed value, wrong bounding-box length, or too many
   repeated values.
2. **The request follows the description, but the server fails.** Examples:
   HTTP 500, a provider crash, an unavailable OTB runtime, or a hidden required
   parameter.
3. **The request is valid, but its data cannot be used.** Examples: an input URL
   the server cannot reach, corrupt base64 data, or a local computer path sent
   to a server-side filename input.
4. **HTTP 200 contains an unusable result.** Examples: a missing output, invalid
   URL text, or a link to a file that does not exist.
5. **An asynchronous job fails later.** HTTP 201 only confirms that the job was
   accepted.

Keep every distinct server error in the deployment captures. The client may
show all of them with the same basic UI: the type of failure followed by the
escaped server message.

## Asynchronous coverage

It is not necessary to run every process through every job state. The job tests
cover this flow once:

```text
POST with Prefer: respond-async
  └─ accepted or running
      ├─ successful → follow the results link
      ├─ failed → show the job message
      └─ DELETE → dismissed or an HTTP error
```

Recorded tests also cover missing job links, invalid JSON, unknown status
values, missing result links, and non-JSON errors.

## Files in a testcase

Each testcase folder contains:

- `testcase.json`: the ordered steps and expected client behavior;
- `NN-name.request.json`: method, URL, headers, and optional body file;
- `NN-name.response.json`: status, headers, final URL, and optional body file;
- a local body file only when the same body is not already stored as a probe or
  captured response.

Source request URLs use `{{baseUrl}}`. The testcase's `deployment` tells tools
which URL to use. Later steps can use values captured from an earlier response:

- `{{jobId}}` and `{{jobUrl}}` for a job;
- `{{resultsUrl}}` for a job result document;
- `{{resultUrl}}` for one linked process output.

In `expected_client_behavior`, `classification` is the short result name.
`must` lists required behavior. `must_not` lists mistakes the test prevents.

## What to compare

For live tests, compare:

- HTTP and job state;
- expected output IDs;
- JSON wrappers and media types;
- whether an output link can be used.

Do not compare changing job IDs, timestamps, temporary filenames, exact error
wording, or every coordinate byte for byte.

Recorded tests can compare their fixed response files exactly.
