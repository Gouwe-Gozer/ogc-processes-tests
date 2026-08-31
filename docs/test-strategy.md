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
| HTTP transport | Injected `fetch`, request forwarding, response envelopes, redirects, aborts, and failures that produced no HTTP response |
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

This repository does not need a provider scenario for every defensive branch
in the client. Its main job is to preserve useful differences observed in real
OGC API Processes services. Controlled conditions that do not depend on a real
provider belong in the future client repository.

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

## Current representative scenarios

The current scenarios are placed under their main client concern. A scenario
can still be reused by tests for another concern.

| Scenario | What it represents |
|---|---|
| `protocol/discovery/weaver-redoak/core-discovery` | Landing page, conformance declaration, and process list from Weaver, captured without CORS response headers |
| `protocol/discovery/weaver-redoak/process-description-forbidden` | An advertised versioned process-description link returns HTTP 403 with HTML |
| `protocol/execution/zoo-local/simple-sync` | Minimal synchronous HTTP 200 execution with one string input and one string result |
| `protocol/execution/pygeoapi-demo/raw-versus-document-response` | A process description plus raw and document results from another implementation |
| `protocol/jobs/zoo-local/successful-job` | Submission, running status, successful status, and result retrieval |
| `protocol/jobs/zoo-local/failed-job` | Accepted submission followed by a failed terminal job state |
| `protocol/jobs/zoo-local/dismiss-running-job` | Accepted submission followed by `DELETE` and a dismissed terminal state |
| `protocol/errors/zoo-local/process-description-html-error` | One process description returns HTTP 500 with HTML instead of JSON |
| `protocol/errors/zoo-local/structured-execution-error` | Synchronous HTTP 500 with a structured JSON problem |
| `protocol/errors/zoo-local/missing-required-input` | Invalid raw request returns a structured HTTP 400 problem |
| `protocol/errors/zoo-local/missing-requested-output` | HTTP 200 response omits an explicitly requested output |
| `forms/validation/directed-local/undocumented-array-length` | An array accepted by the published schema is rejected because the provider requires an undocumented length |
| `results/maps/zoo-local/geojson-value` | Synchronous execution with referenced GeoJSON input, a numeric literal, and wrapped GeoJSON output |
| `results/downloads/zoo-local/result-by-reference` | Synchronous result returned as an `href` with a media type |

Each request file contains its method, URL, headers, and body. Each response
file contains its status, headers, final URL, and body. The README explains why
the exchange matters.

## Evidence not promoted yet

The remaining recorded exchanges are still useful, but they do not currently
require another protocol-core scenario:

| Evidence group | Why it remains evidence |
|---|---|
| Similar GEOS and SAGA executions | They use request and result envelopes already represented by the selected synchronous scenarios |
| Additional SAGA, GDAL, R, and OTB crashes | Their messages differ, but the core handles them through the selected structured HTTP-error path |
| Unknown jobs, premature results, and repeated dismissal | They are useful diagnostics but do not change the normal job flow selected above |
| Bounding boxes, enums, repeated inputs, and nested schemas | Promote when form-generation tests begin |
| Large CSV, deeply nested JSON, raster, and multiple-output results | Promote when result-handling tests begin; the CLIMADA evidence records its 18.8 MB CSV without checking the full body into Git |
| Server-side filenames and unavailable result downloads | Provider-specific evidence unless a target implementation requires client support |

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
- invalid input according to the process description;
- input allowed by the description but rejected by an undocumented provider
  rule.

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
scenarios are grouped by client concern, specific behaviour, provider, and
scenario. This keeps provider differences visible while allowing pygeoapi,
Weaver, ZOO, and future services to appear under the same behaviour.

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

Test the real HTTP adapter separately with an injected `fetch`. Those tests
should cover request-option forwarding, HTTP responses including 4xx and 5xx,
redirected final URLs, rejected requests, and aborts. They do not need a real
OGC provider or a scenario folder here.

### Provider evidence and controlled client tests

Some important client behaviours may never appear in the selected live
services. Do not invent provider evidence for them. Test them later with
controlled responses in the client project.

| Behaviour | Where it should be tested | When it belongs here |
|---|---|---|
| Resolve relative links against the final response URL | Protocol-core unit test | Keep a real capture if a provider advertises relative links |
| Preserve requested and redirected final URLs | HTTP transport unit test | Keep a real redirect only when it helps explain a provider |
| Continue when one process description fails | Protocol-core unit test using several controlled responses | Keep each real failing description as provider evidence |
| Read `Location` without depending on capitalization | HTTP transport or job unit test | No separate provider scenario is needed |
| Use a body monitor link when `Location` is absent | Async-job unit test | Keep a real capture if a provider behaves this way |
| Reject an accepted job with no usable monitor location | Async-job unit test | Keep a real capture if encountered |
| Handle network failure and `AbortSignal` | HTTP transport unit test | Not provider evidence because no HTTP response exists |
| Stop polling without dismissing the server job | Polling unit test | A live smoke test may confirm it, but no recorded response can prove it |
| Detect CORS restrictions and use a relay when required | Browser integration and live provider test | Response headers and affected providers are useful evidence here |
| Subscriber callbacks and version selection | Client feature and integration tests if these commitments remain in scope | Add provider evidence only for services that expose these capabilities |

### Current evidence audit

The evidence was checked for these behaviours on 31 August 2026:

| Behaviour | What is currently recorded |
|---|---|
| Relative links | None. All recorded `href` values are absolute URLs or placeholders for absolute URLs |
| Redirected final URLs | None. Recorded request and final URLs match, and no HTTP 3xx exchange is stored |
| Advertised endpoints unavailable | ZOO returns HTTP 500 for `OTB.ReadImageInfo`; RedOak's nginx gateway returns HTTP 403 for an advertised description, execution, and job-list endpoint. Only the process-description failures are selected scenarios |
| Missing or unusable async location | Every recorded HTTP 201 response contains `Location`. The DIRECTED accepted-job body has no monitor link, so it confirms that the client must also read the header. No capture omits both locations |
| Results requested too early | Local Weaver returns HTTP 404 with a structured `JobResultsNotReady` body, `cause.status: accepted`, and monitoring links. This is a temporary job state, not an unknown resource |
| Different `Location` capitalization | None. All captures use `Location` |
| Error content negotiation | Local Weaver returns a structured JSON 404 for an unknown process when JSON is requested, and an HTML 404 for the same URL without that `Accept` header |
| Input-validation errors | Local Weaver reports missing-input cardinality as structured JSON. An incomplete request with an invalid enum reports only the next missing input, while an invalid type produces a generic failed job without identifying the bad field |
| Successful Weaver execution | `EchoProcess` is captured in sync and async mode with inline and referenced outputs. Some referenced output URLs return HTTP 403 even though the job is successful |
| CORS differences | Both Weaver deployments and ZOO lack usable CORS permission for the tested execution request. BGT and DIRECTED pass the preflight. The public pygeoapi demo does not allow `content-type` or `prefer` |
| Network failure and abort | Not recordable as provider responses because no HTTP response is produced |
| Callbacks | Both Weaver deployments advertise callback conformance, but there is no callback execution capture |
| OGC API Processes parts | Both Weaver deployments advertise conformance classes from Parts 1, 2, 3, and 4, but the evidence does not exercise client selection or the additional operations |

The Weaver conformance responses therefore suggest two possible future
evidence runs: callback execution and the additional Processes-part operations.
RedOak blocks public process descriptions with HTTP 403. The local deployment
now provides successful sync, async, polling, and result evidence.

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
| Process discovery and descriptions | Discovery and process-description evidence exists for ZOO, both Weaver deployments, and all three pygeoapi deployments. The selected scenario set remains intentionally smaller |
| Generated forms | Partial: descriptions contain required inputs, enums, bounding boxes, primitive types, and an array without item details that requires raw JSON fallback; generated UI behaviour must be tested in the client project |
| Raw JSON fallback | The pygeoapi raw-versus-document scenario preserves a description/result mismatch for this path |
| Synchronous execution | Inline document, raw, and referenced results are selected |
| Async submission, polling, results, and dismiss | Successful, failed, and dismissed job flows are selected |
| Result rendering | Result samples and measured large-CSV evidence exist, but choosing a map, inline view, JSON view, or download must be tested in the application |
| CORS and exposed `Location` | Provider diagnostics record execution preflights for all six deployments. BGT and DIRECTED pass; ZOO, both Weaver deployments, and the public demo require a relay for the tested execution request. Browser integration still belongs in the client project |
| Subscriber callbacks and polling reconciliation | Weaver advertises callback conformance and ZOO polling flows are selected, but no callback request has been captured |
| OGC API Processes v1 and v2 selection | Weaver advertises conformance classes from multiple OGC API Processes parts, but no client selection behaviour has been captured |
| Different server implementations | Provider evidence covers ZOO, three pygeoapi deployments, and both public and local Weaver. The smaller selected scenario set uses only cases with distinct client behaviour |
| Interoperability matrix | The evidence can supply observations, but the matrix has not been created yet |
