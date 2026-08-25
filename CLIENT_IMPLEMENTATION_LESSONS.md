# Client implementation lessons learned

## Purpose and tender scope

This document records lessons from the 50 selected process entries and their 53
execution or description cases in this
repository for the Topic 3 OGC API - Processes client. It focuses on:

- what the protocol core can distil from a process description;
- which assumptions are safe when creating an execution request;
- what can go wrong when an end user supplies incorrect input;
- the minimum boundary needed between the protocol core and HTTP transport.

The findings are based on the captured ZOO-Project descriptions in
[`evidence/zoo/`](evidence/zoo/), the canonical requests in [`cases/`](cases/),
and their observed executions. They describe the current tested server profile,
not every OGC API - Processes implementation. See
[`SERVER_PROFILE_COMPATIBILITY.md`](SERVER_PROFILE_COMPATIBILITY.md) for the
profile and upgrade implications.

This is not a plan for a general-purpose API client. Features should be added
only when they are required by a Topic 3 commitment or by a tested service.

## Intended architecture

```text
Consumer / application
├── form generation                 outside the protocol core
├── raw JSON editor                 outside the protocol core
├── MapLibre integration            outside the protocol core
└── result rendering                outside the protocol core
             │
             ▼
OGC API - Processes protocol core
├── landing page and link discovery
├── conformance
├── process collection and descriptions
├── synchronous execution
├── asynchronous jobs and results
└── job dismissal
             │
             ▼
Minimal transport port
├── browser fetch adapter           required
└── relay adapter                   optional, only if later required
```

The protocol core must not call browser `fetch` directly. It depends on a
small transport interface so the same protocol behaviour can later run through
a relay if browser access to a tested service requires it.

Form controls, map behaviour, and rendering decisions consume the protocol
core but are not part of it. The core exposes the raw and understood parts of a
process description; it does not need to know how they are presented.

## Minimal transport boundary

The transport exists only to decouple protocol logic from browser `fetch`. It
needs to support:

- methods `GET`, `POST`, and `DELETE`;
- request URL and headers;
- an optional request body;
- an optional `AbortSignal`;
- response status, headers, final URL, and raw body.

An implementation-neutral shape could be:

```ts
type HeaderMap = Record<string, string>;

interface TransportRequest {
  method: "GET" | "POST" | "DELETE";
  url: string;
  headers?: HeaderMap;
  body?: string | Uint8Array;
  signal?: AbortSignal;
}

interface TransportResponse {
  status: number;
  headers: HeaderMap;
  url: string;
  rawBody: Uint8Array;
}

interface Transport {
  request(request: TransportRequest): Promise<TransportResponse>;
}
```

The transport should return HTTP error responses as responses. For example,
HTTP 400 or 500 is not a network failure and its raw body is needed by the
protocol core to parse an OGC problem response. A rejected transport promise
is reserved for failures where no HTTP response was obtained or the request
was aborted.

JSON encoding, OGC problem parsing, link interpretation, and job behaviour
belong to the protocol core. This keeps a future relay adapter small and avoids
duplicating protocol behaviour in two transports.

### What can be borrowed from `examples/ogc-client`

The existing `examples/ogc-client` is useful as a source of small, tested
ideas:

- injecting request headers and browser fetch options;
- returning typed endpoint failures;
- resolving relative links against a response or API URL;
- testing network, HTTP, parsing, and abort behaviour separately.

Its transport utility should not be copied unchanged. It uses global fetch
options, concentrates on shared GET and XML requests, and does not expose the
response information needed for asynchronous OGC API execution. The new port
should be instance-scoped and JSON-neutral. Concurrent-request deduplication
and its browser cache are not necessary for the tender core.

If source code is copied rather than merely using the same ideas, retain the
BSD-3-Clause copyright notice and licence required by that project.

### Deliberately not part of the transport

Do not add the following without a demonstrated requirement:

- an OAuth or other authentication framework;
- automatic retries or backoff;
- TLS or proxy configuration;
- caching infrastructure;
- download persistence;
- observability frameworks or request history;
- provider-profile adapters.

Headers are deliberately supported, so a consuming application can provide a
service-specific header if one is required. That does not justify building
speculative OAuth. Likewise, a relay transport remains a small optional future
adapter, not a general proxy subsystem.

## Protocol-core responsibilities

### Landing page and discovery

The core starts at the configured API URL, parses the landing page, and follows
advertised link relations for conformance and processes. Relative links are
resolved against the URL of the document that contained them.

The captured server sometimes advertises absolute URLs containing `localhost`.
Those links may be unusable when the API is reached through another hostname.
The core should retain the advertised link and provide a clear failure. A
configurable link-rewrite or relay policy is an optional integration feature
only if a tested deployment requires it.

### Conformance

The core fetches `/conformance` through its discovered link and exposes the
advertised conformance classes. It should use those capabilities before
offering protocol operations, rather than treating one ZOO-Project profile as
the definition of the standard.

### Processes and descriptions

The core fetches the process collection and individual process descriptions.
It retains each raw description and normalizes the subset needed by the
consumer. Unknown fields or unsupported schema constructs must not crash
discovery.

When a schema construct is unsupported, the promised fallback is raw JSON. The
core reports that it cannot interpret that part of the schema and retains it;
the consumer can offer a raw JSON editor and pass the resulting valid JSON to
execution. The core should not silently weaken or invent schema constraints.

### Execution

The core serializes or accepts an execute request body and posts it to the
advertised execution endpoint. It supports:

- synchronous document responses;
- asynchronous submission using the required preference header;
- output transmission by value or reference where advertised.

HTTP 200 normally means the tested synchronous execution has completed and the
body contains its result document. It does not mean a job is waiting elsewhere
unless the response explicitly describes a job.

HTTP 201 for asynchronous submission means the job was accepted, not that it
succeeded. The core obtains the job location from the response headers or body
and exposes the job resource.

### Jobs, results, and dismiss

The core can retrieve job status, follow a successful job's result link, and
request dismissal with `DELETE` when supported. It recognizes non-terminal and
terminal states without requiring UI-specific polling or progress components.

A small convenience operation may poll until a terminal state while accepting
an `AbortSignal`. Elaborate scheduling, persistence, and retry infrastructure
are outside scope. The application remains free to control when status is
requested.

## What can be distilled from a process description

### Process identity and operation links

A description supplies an exact process `id`, human-readable `title` and
`description`, a `version`, metadata, and links. The execute link is identified
by its relation, for example:

```text
http://www.opengis.net/def/rel/ogc/1.0/execute
```

Process, input, and output IDs are opaque and case-sensitive. The core must not
translate or derive them from titles.

### Execution and output capabilities

`jobControlOptions` advertises capabilities such as:

- `sync-execute`;
- `async-execute`;
- `dismiss`.

`outputTransmission` advertises `value`, `reference`, or both. These fields are
the basis for execution choices exposed to the consumer. The request and HTTP
headers still select the actual mode.

### Input identifiers, requiredness, and cardinality

The `inputs` object gives the exact execution-request keys. In the captured
profile, inputs with `minOccurs: 0` are optional and inputs without that
override behave as required. `maxOccurs` can indicate repeatable inputs,
including `unbounded`.

Requiredness, nullability, and defaulting are different:

- optional means the input may be omitted;
- `nullable: true` advertises that explicit JSON `null` is accepted;
- `default` advertises a value the server may apply;
- repeatable values must not lose order.

The normalized model must preserve these distinctions. It must not replace an
omitted value with `null` or lose valid values such as `0`, `false`, or an
empty string.

### Literal and structured schemas

The captured descriptions demonstrate `string`, `integer`, `number`,
`boolean`, `object`, and array values. Constraints include:

- `default`, `enum`, `format`, and `nullable`;
- `oneOf` and `allOf`;
- nested `required` and `properties`;
- `items`, `minItems`, and `maxItems`.

For example, `EchoProcess` describes a bounding-box object with a four- or
six-number `bbox` array and an enumerated `crs` URI.

The core may normalize schema features it understands. Form generation remains
outside the core, and unsupported constructs remain available through the raw
description and raw JSON fallback.

### Complex values and references

The captured descriptions include:

- inline JSON objects;
- inline UTF-8 XML strings;
- base64-encoded XML strings;
- references to remotely available data;
- media types and, sometimes, a content schema.

A current reference request has this form:

```json
{
  "href": "https://example.test/input.geojson",
  "type": "application/json"
}
```

An inline complex value may require a wrapper:

```json
{
  "value": {
    "type": "FeatureCollection",
    "features": []
  }
}
```

Inline/reference transport, content format, and content encoding are separate
properties. The core should preserve the advertised wrapper rather than infer
it from a filename extension.

### Outputs

The `outputs` object supplies exact output IDs and value schemas. Together with
`outputTransmission`, it describes available value/reference and format
choices. A tested document response requests an output like this:

```json
{
  "outputs": {
    "Result": {
      "format": {"mediaType": "application/json"},
      "transmissionMode": "value"
    }
  },
  "response": "document"
}
```

The core must not assume that every output is called `Result`. A string output
may contain ordinary text, a server-side path, or a download URL. The core
returns the result and its representation metadata; rendering it as text,
GeoJSON, GML, raster, or a MapLibre layer is outside the core.

## Reasonably safe assumptions

After successfully fetching the target server's current description, it is
reasonable to assume that:

- advertised process, input, and output IDs are the identifiers to serialize;
- advertised primitive types and explicit constraints are the basis for
  validation of understood schema constructs;
- inputs explicitly marked with `minOccurs: 0` may be omitted;
- only advertised job-control and transmission modes should be used by default;
- an advertised default may be shown, but the server decides whether an
  omitted optional input receives it;
- an advertised media type is a candidate representation, not proof that any
  document carrying that type is semantically valid;
- an accepted asynchronous execution must be followed to a terminal job state.

## Unsafe assumptions and observed mismatches

### The description does not guarantee execution

`Gdal_Grid` advertises only `OF`, `InputDSN`, and `OutputDSN`. A request using
exactly those fields conforms to the description, but the provider requires
additional unadvertised parameters and returns HTTP 500. The core must not
invent provider-specific inputs to make it work.

`Gdal_Dem` has a similar problem for its hillshade branch, which needs an
unadvertised value. The verified case uses its advertised slope branch.

### A broad complex schema may hide narrower provider rules

The `Distance` provider rejected point GML despite generic geometry wording;
the executable case uses polygons. A matching media type and valid XML or JSON
cannot prove that the provider accepts the geometry or document structure.

Metadata can also conflict internally. A title may describe a generic geometry
while a content schema identifies a polygon. The core should retain both and
must not claim certainty it does not have.

### A string may represent a server-side filename

The tested GDAL/OGR descriptions expose data-source inputs as strings. Their
values are paths resolved inside the ZOO container, not browser uploads or
paths on the end user's computer. Local fixture staging is test infrastructure
for this deployment, not a portable client capability.

### A reference may not be reachable from the process server

A URL reachable by the browser may still be inaccessible to the process server
because it executes in a different network context. Only execution proves that
the provider can retrieve and use the reference.

An origin policy or relay may become relevant for a concrete deployment. It is
optional until the tender commitments or a tested service require it.

### Output references may be malformed

The observed `Ogr2Ogr` response concatenated two URLs into one malformed value.
The core must not assume every returned string is a valid URL. It should retain
the raw output so the consumer can report or inspect it.

### Provider errors may be generic or misleading

Observed failures use a generic `NoApplicableCode` problem with free-text
`detail`; one supplies no useful provider message. Bad input can surface as
HTTP 500 rather than a precise 4xx response. The core must preserve status,
headers, and raw body even when problem parsing succeeds.

The SAGA cases add two reusable but coarse diagnostics: provider termination by
`SIGSEGV` and by `SIGABRT`. These safely support a warning that the server-side
process crashed or aborted. They do not safely identify which input was wrong:
the same `SIGSEGV` text occurs for distinct repeated-raster, interpolation, and
point-cloud requests. All distinct observed messages, their occurrences, and
safe client interpretations are maintained in
[`evidence/zoo/ERROR_CATALOG.md`](evidence/zoo/ERROR_CATALOG.md).

### HTTP success can still contain an unusable result

Two SAGA requests returned HTTP 200 with `{}` even though an output was
requested. Another returned a TIFF reference for a table result, but the target
TIFF did not exist. Status alone is therefore insufficient: the core should
retain the response and expose its parsed outputs, while the consumer may warn
when a requested output identifier is absent or a selected reference cannot be
retrieved. It must not silently convert such a response into fabricated data.

### Input and output identifiers use separate namespaces

The generated OTB descriptions can expose the same identifier in both
`inputs` and `outputs`. For example, `OTB.BandMath` uses input `out` to select
the output pixel type and output `out` for the resulting image. A normalized
model must therefore keep inputs and outputs separate rather than enforcing
global identifier uniqueness.

OTB descriptions also flatten conditional application metadata. Rasterization
marks fields from two mutually exclusive modes as required, while Segmentation
marks parameters from inactive filter and output branches as required. The core
must preserve that metadata, but a consumer should avoid claiming that it has
fully understood conditionality that the description does not encode.

### One process description can fail independently

The collection advertises `OTB.ReadImageInfo`, but its individual description
returns HTTP 500 HTML after the CGI loader receives `SIGSEGV`. Other process
descriptions remain usable. Discovery should therefore report the individual
failure without discarding the entire process collection and must retain a
non-JSON error body.

Five other OTB descriptions load, but execution returns `InternalError: No OTB
Application found.` before fixtures are processed. The same fixtures and
parameters succeed through OTB CLI 7.0. This supports a server-runtime warning,
not an input-validation warning.

## Handling incorrect end-user input

The protocol core should validate only what it understands and what is useful
for constructing a valid protocol request. UI-specific validation and form
messages remain the consumer's responsibility.

### Request-envelope validation

Before submission, the core can verify that:

- the execute body is valid JSON;
- `inputs` and `outputs`, when present, have the expected object shape;
- known input/output IDs match the current process description;
- required understood inputs are present;
- requested execution and transmission modes are advertised;
- an async request carries the required preference header.

Unknown fields or unsupported schemas should not be silently discarded. In
raw JSON mode, the core may submit a syntactically valid request while marking
that it could not completely validate it against the description. This is the
required escape hatch for incomplete descriptions and unsupported schemas.

### Validation of understood values

For schema constructs it supports, the core or consuming UI can check:

- primitive JSON types without broad implicit coercion;
- required versus nullable values;
- enums, array sizes, and cardinality;
- nested required properties such as `bbox` and `crs`;
- the chosen `oneOf` alternative;
- complex-value wrappers, media type, and encoding.

Values such as `0` and `false` must be preserved. An untouched advertised
default should not automatically become an explicitly submitted value.

Format-specific semantic checks, coordinate transformations, CRS conversion,
and geometry repair are not responsibilities of the protocol core. Simple
checks can be added in the consumer where they are directly required, but the
client must not silently change the user's data.

### Errors and responses

The core should distinguish only the failure categories needed by its callers:

- transport failure or abort, where no HTTP response was obtained;
- non-success HTTP response, retaining status, headers, final URL, and body;
- invalid JSON or an invalid expected protocol document;
- failed or dismissed asynchronous job.

Where possible, it may parse `title`, `type`, and `detail` from an OGC problem
response. The raw body remains available because provider messages can be
incomplete. An error should be associated with an input only when the server
identifies that input unambiguously.

For HTTP 200, parse the body using its actual `Content-Type` and expected
protocol resource. Retain unknown outputs for forward compatibility. For HTTP
201, locate and expose the job, then use job status to determine eventual
success or failure.

## Relationship to the generated Postman collection

The implemented collection layout is:

```text
OGC API Processes tests
├── POST_process_sync
│   └── <case folder name>
└── process_descriptions
    └── <process_id>
```

It supports the protocol-core work because:

- each canonical request is an executable POST example;
- each represented process has one deduplicated description GET;
- bodies are copied exactly from `cases/<name>/request.json`;
- asynchronous `Prefer` headers are preserved;
- advertised descriptions and observed executions can be compared directly.

Despite its historical name, `POST_process_sync` also contains asynchronous
cases. The protocol core must infer mode from the request and response, not the
folder name. Renaming it to `POST_process_execution`, or separating sync and
async examples, is an optional future cleanup.

The collection is generated test material, not the client contract. The source
of truth remains each `case.json`, `request.json`, fixture, captured process
description, and observed response.

## Scope-aligned implementation plan

1. Define the minimal transport port and implement the browser `fetch` adapter.
2. Implement landing-page link discovery and `/conformance` handling.
3. Implement process collection and description retrieval, retaining raw JSON.
4. Normalize the schema subset needed by Topic 3 and expose raw JSON fallback
   for unsupported constructs.
5. Implement synchronous execution and response parsing.
6. Implement asynchronous submission, job status, results, and dismissal.
7. Verify the core through the canonical success, expected-error, and async
   cases in this repository.
8. Add a relay transport or another optional integration only when a committed
   use case or tested service demonstrates the need.

The first implementation should stop there. Form generation, MapLibre
integration, and result rendering belong to their respective application
layers. Authentication frameworks, retries, caching, persistence,
observability, and provider-specific workarounds remain optional future work,
not hidden requirements of the protocol core.
