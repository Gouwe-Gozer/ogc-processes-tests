# Repository scope and future test strategy

## End goal

This repository prepares representative OGC API Processes material that will
eventually be used by the client's automated test suite. It should cover:

- different OGC API Processes implementations;
- discovery, descriptions, synchronous execution, asynchronous jobs, and
  errors;
- process descriptions with different input schemas for generated forms;
- results that need different presentation, such as maps, JSON views, text,
  and downloads.

The future client tests should be separated by concern:

| Test area | What it should verify |
|---|---|
| Protocol core | HTTP requests, discovery, execution, job transitions, links, and errors |
| Form generation | How process-description schemas become form fields and when raw JSON fallback is needed |
| Result handling | How output descriptions and returned media types select maps, JSON views, text, or downloads |
| Live provider compatibility | A small smoke set against each real implementation |

One recorded exchange may support several test areas. Do not duplicate it just
to place it under several headings.

## Scope of this repository now

For now, this repository should:

- capture real process descriptions, requests, responses, headers, and final
  URLs;
- keep a small representative set under [`../scenarios/`](../scenarios/);
- keep similar processes and provider-specific observations under
  [`../evidence/`](../evidence/);
- provide fixtures and Postman collections for inspecting live APIs;
- record enough provider information to understand where an exchange came
  from.

The contents of `scenarios/` are future test material, but they are not
executable client tests yet.

## Decisions that wait for the client

Do not build a test framework in this repository before the client has a
public API, module boundaries, and a TypeScript test runner. In particular,
wait before deciding:

- whether `scenarios/` eventually moves into the client repository or remains
  an external fixture set;
- the fake transport implementation and its response queue;
- assertion helpers or a machine-readable testcase manifest;
- the final folder layout of protocol, form, result, and live tests;
- the interfaces used by form generation and result rendering.

Those decisions should follow the actual client design. Until then, plain JSON
records and short README files are sufficient.

## Current main scenarios

The current scenarios establish the file format:

| Scenario | What it represents |
|---|---|
| `sync/zoo-local/geojson-value` | Synchronous execution with referenced GeoJSON input, a numeric literal, and wrapped GeoJSON output |
| `async/zoo-local/successful-job` | Submission, running status, successful status, and result retrieval |
| `errors/synthetic/non-json-error` | An HTTP 500 response containing HTML instead of an OGC JSON problem |

Each request file contains its method, URL, headers, and body. Each response
file contains its status, headers, final URL, and body. The README explains why
the exchange matters.

## Choosing the rest of the main set

Add a scenario when it introduces a different client-facing behaviour:

- a new input shape needed by form generation;
- a new response mode or output shape;
- a different asynchronous job transition;
- an error or malformed response that requires different handling;
- an unsupported schema that must fall back to raw JSON.

Do not add another main scenario only because it uses a different processing
library or algorithm. Similar requests remain available under `evidence/`.

The final number is determined by coverage rather than a fixed target. The set
should eventually include:

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

Requests alone are not enough for UI tests. A form-generation scenario needs
the process description. A result-handling scenario needs the output
description and an actual returned value or reference, including its media
type when available.

## Adding server implementations

Evidence remains grouped by provider because it records what one deployment
did. For each additional implementation, collect only the useful minimum:

- landing page, conformance response, and process list;
- at least one representative process description;
- one synchronous execution when supported;
- one asynchronous flow when supported;
- one useful error or provider-specific response shape.

Do not repeat every process and data shape for every implementation. Curated
scenarios are grouped by behaviour, then provider, then scenario. This makes
provider differences visible without prescribing the future client test
folder layout.

This folder structure does not prescribe a fake transport interface. A future
fake transport can load the request and response sequence from any selected
scenario after the client's real transport contract has been defined.

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
| Broken process description | `OTB.ReadImageInfo` | one unavailable-description scenario |

## Bad input and bad responses

Keep evidence from these groups, but only promote a response to `scenarios/`
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

After the client exists, deterministic protocol tests can call its public API
with a small fake transport. The fake transport will return the recorded
responses while the test checks the requests made and values returned. The
fake belongs in the client test suite, not in this repository today.

Form tests should load recorded process descriptions and check the client's
form model. Result tests should load recorded output descriptions and values
and check the selected presentation. Those tests should use the same source
material where possible.

Live tests should call a small selection through the real browser transport
against ZOO, pygeoapi, or a testbed service. Compare stable properties such as
status, job state, output IDs, media types, and usable links. Do not compare
job IDs, timestamps, temporary filenames, exact coordinates, or exact error
wording.

Postman and `run_evidence_request.py` are useful for inspecting a server. They
bypass the client and therefore do not count as client tests.

## Coverage of the Topic 3 plan

This table describes available source material. It is not a request to
implement missing client features in this repository. A feature is verified
only when an actual client test uses the material.

| Topic 3 commitment | Coverage in this repository |
|---|---|
| Process discovery and descriptions | Partial: many descriptions are captured, but landing-page, conformance, and process-list scenarios are still missing |
| Generated forms | Partial: descriptions contain required inputs, enums, bounding boxes, and primitive types, but generated UI behaviour must be tested in the client project |
| Raw JSON fallback | Documented, but no main scenario has been selected yet |
| Synchronous execution | A main GeoJSON scenario and broader supporting evidence are available |
| Async submission, polling, results, and dismiss | Async success is a main scenario; failure and dismissal remain in supporting evidence |
| Result rendering | Result samples exist, but choosing a map, inline view, JSON view, or download must be tested in the application |
| CORS and exposed `Location` | Missing |
| Subscriber callbacks and polling reconciliation | Missing |
| OGC API Processes v1 and v2 selection | Missing |
| Different server implementations | Limited: ZOO supplies most live evidence; two pygeoapi servers supply recorded response shapes |
| Interoperability matrix | The evidence can supply observations, but the matrix has not been created yet |
