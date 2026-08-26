# Selecting and using examples

## Purpose

The goal of this repository is to collect a small set of representative OGC
API Processes requests and responses that our client should handle.

There are two levels:

- [`../examples/`](../examples/) is the main set used while implementing and
  testing the client.
- [`../evidence/`](../evidence/) keeps similar processes, provider-specific
  failures, process descriptions, and other observations that may be useful
  later.

The examples are fixtures, not an independent test framework. The client
project should load them and make assertions with its normal TypeScript test
tools.

## Current main examples

The first three examples establish the format:

| Example | What it represents |
|---|---|
| `sync/geojson-value` | Synchronous execution with referenced GeoJSON input, a numeric literal, and wrapped GeoJSON output |
| `async/successful-job` | Submission, running status, successful status, and result retrieval |
| `errors/non-json-error` | An HTTP 500 response containing HTML instead of an OGC JSON problem |

Each request file contains its method, URL, headers, and body. Each response
file contains its status, headers, final URL, and body. The README explains why
the exchange matters.

## Choosing the rest of the main set

Add an example when it introduces a different client-facing behaviour:

- a new input shape needed by form generation;
- a new response mode or output shape;
- a different asynchronous job transition;
- an error or malformed response that requires different handling;
- an unsupported schema that must fall back to raw JSON.

Do not add another main example only because it uses a different processing
library or algorithm. Similar requests remain available under `evidence/`.

A useful final main set will probably contain 12–15 examples, including:

- a simple process description;
- a complex or unsupported schema;
- simple synchronous JSON;
- GeoJSON input and output;
- raw and document responses;
- deeply nested JSON;
- an output returned by reference;
- async success, failure, and dismissal;
- a structured OGC error;
- a non-JSON error;
- HTTP 200 with a missing or unusable output;
- an accepted job without a usable location;
- invalid input according to the process description.

## Process families found in the ZOO evidence

Many ZOO processes use the same client-facing shapes. The full request and
response material remains in [`../evidence/zoo-local/`](../evidence/zoo-local/).

| Request or result shape | Processes considered | Representative candidates |
|---|---|---|
| Simple text input and output | `hellojs` | `hellojs` |
| Mixed text, JSON, and bounding box | `EchoProcess` | `EchoProcess` |
| Asynchronous job | `longProcess`, `demo` | both, because one succeeds and one fails |
| Geometry to number or Boolean | `GetArea`, `Distance`, `Contains`, `IsValid` | `Distance` or `Contains` |
| One geometry to one geometry | GEOS and SAGA single-input tools | `Buffer` |
| Two geometries to one geometry | GEOS and SAGA two-input tools | `Intersection` |
| Filenames inside the server | GDAL and OGR wrappers | evidence only unless a target service requires this pattern |
| Raster to raster | SAGA grid tools and `OTB.BandMath` | one success and one useful failure |
| Vector or LAS to raster | SAGA point-cloud tools and OTB rasterization | one request if its result shape is needed |
| Several named vector outputs | SAGA shape/TIN tools and OTB segmentation | SAGA contours |
| CSV, table, or XML output | SAGA table/statistics and OTB statistics | one usable reference output |
| Immediate server error | `failR` | `failR` |
| Broken process description | `OTB.ReadImageInfo` | one unavailable-description example |

## Bad input and bad responses

Keep evidence from these groups, but only promote a response to `examples/`
when it requires distinct client behaviour:

1. The client can identify invalid input from the process description.
2. The request follows the description, but the server fails.
3. The request is valid, but the processing software cannot use its data.
4. HTTP 200 contains a missing or unusable output.
5. An asynchronous job fails after its submission was accepted.

Several different server errors may all use the same client handling:

```text
Request failed — server message: “<server detail>”
Job failed — server message: “<job message>”
```

Keep the distinct raw messages under `evidence/`; do not create
provider-specific client code for them.

## Using the files in client tests

Recorded tests should call the client's public API with a fake implementation
of its small HTTP transport. The fake transport returns a response from an
example, after which the TypeScript test checks the client result.

Live tests should call a small selection through the real browser transport
against ZOO, pygeoapi, or a testbed service. Compare stable properties such as
status, job state, output IDs, media types, and usable links. Do not compare
job IDs, timestamps, temporary filenames, exact coordinates, or exact error
wording.

Postman and `run_evidence_request.py` are useful for inspecting a server. They
bypass the client and therefore do not count as client tests.

## Coverage of the Topic 3 plan

This table describes test material in this repository. A feature is verified
only when an actual client test uses that material.

| Topic 3 commitment | Coverage in this repository |
|---|---|
| Process discovery and descriptions | Partial: many descriptions are captured, but landing-page, conformance, and process-list examples are still missing |
| Generated forms | Partial: descriptions contain required inputs, enums, bounding boxes, and primitive types, but generated UI behaviour must be tested in the client project |
| Raw JSON fallback | Documented, but no main example has been selected yet |
| Synchronous execution | A main GeoJSON example and broader supporting evidence are available |
| Async submission, polling, results, and dismiss | Async success is a main example; failure and dismissal remain in supporting evidence |
| Result rendering | Result samples exist, but choosing a map, inline view, JSON view, or download must be tested in the application |
| CORS and exposed `Location` | Missing |
| Subscriber callbacks and polling reconciliation | Missing |
| OGC API Processes v1 and v2 selection | Missing |
| Different server implementations | Limited: ZOO supplies most live evidence; two pygeoapi servers supply recorded response shapes |
| Interoperability matrix | The evidence can supply observations, but the matrix has not been created yet |
