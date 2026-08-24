# Client implementation lessons learned

## Purpose and scope

This document records lessons from the first 26 process cases in this
repository. It focuses on what a generic OGC API - Processes client can learn
from a process description, which assumptions are safe, and how the client
should handle invalid or incompatible user input.

These findings are based on the captured ZOO-Project descriptions in
[`evidence/zoo/`](evidence/zoo/), the canonical requests in [`cases/`](cases/),
and their observed executions. They describe the current server profile, not
every OGC API - Processes implementation. See
[`SERVER_PROFILE_COMPATIBILITY.md`](SERVER_PROFILE_COMPATIBILITY.md) for the
profile and upgrade implications.

## Main conclusion

A process description is the best available contract for constructing an
execution request, but it is not proof that the process implementation honours
that contract.

The client should therefore separate three concerns:

1. **Description parsing:** turn advertised metadata and schemas into a usable
   internal model.
2. **Request validation:** catch errors that are demonstrably inconsistent with
   that model.
3. **Execution handling:** submit the request and robustly handle provider
   errors, asynchronous jobs, and malformed responses.

Passing client-side validation means "consistent with the advertised
description". It must never be presented as a guarantee that execution will
succeed.

## What can be distilled from a process description

### Process identity and operation links

The description supplies an exact process `id`, a human-readable `title` and
`description`, a `version`, and links. The execute link is identified by its
relation, for example:

```text
http://www.opengis.net/def/rel/ogc/1.0/execute
```

The client can use this information to label the process, identify the
contract version, and locate the execution endpoint. Process and input IDs are
opaque and case-sensitive; they must not be translated, normalized, or derived
from titles.

Links require a client policy. The captured server sometimes emits absolute
URLs containing `localhost`, which may be unusable behind a proxy or from a
different host. Prefer a matching advertised link when it is usable, but check
its origin against the configured API endpoint. A client must not blindly send
credentials to, or make server-side requests through, an unexpected origin.

### Supported execution and output modes

`jobControlOptions` advertises capabilities such as:

- `sync-execute`;
- `async-execute`;
- `dismiss`.

`outputTransmission` advertises `value`, `reference`, or both. These values can
drive the available controls in the client. They do not determine the mode by
themselves: the execution request and HTTP headers still select the requested
behaviour.

In the current tests, synchronous execution normally returns HTTP 200 with the
result document. Asynchronous submission returns HTTP 201 and a job location.
HTTP 201 only means that the job was accepted; the job may later become
`successful` or `failed`. The client must poll the advertised monitor link and
only fetch results after a successful terminal state.

### Input identifiers and requiredness

The `inputs` object gives the exact request keys. For this profile, inputs with
`minOccurs: 0` are optional and inputs without that override behave as required
inputs. `maxOccurs` can indicate repeatable values, including `unbounded`.

Requiredness, nullability, and defaulting are separate concepts:

- optional means the input may be omitted;
- `nullable: true` means an explicit JSON `null` is allowed by the advertised
  schema;
- `default` describes a server-side default and does not make a required input
  optional unless the surrounding contract says so;
- repeatable input values should be represented without losing order.

The client should preserve these distinctions in its internal model. In
particular, it must not convert an omitted value into `null`, or accidentally
drop valid values such as `0`, `false`, or an empty string.

### Literal types and constraints

The captured schemas demonstrate `string`, `integer`, `number`, `boolean`, and
`object` values. They may also include:

- `default`;
- `enum`;
- `format`, such as `float`, `double`, or `uri`;
- `nullable`;
- `oneOf` and `allOf`;
- nested `required` and `properties`;
- array `items`, `minItems`, and `maxItems`.

These are suitable for generating form controls and local validation. For
example, `EchoProcess` describes a bounding box object with a four- or
six-number `bbox` array and an enumerated `crs` URI.

Unknown schema keywords must be retained or ignored safely. They must not make
the whole description unparsable. Conversely, a client must not silently
weaken a constraint merely because its form renderer does not support it.

### Complex data, representations, and references

Complex inputs and outputs are commonly expressed with `oneOf`. The captured
descriptions include:

- inline JSON objects;
- inline UTF-8 XML strings;
- base64-encoded XML strings;
- link objects for referenced data;
- media types and, sometimes, a content schema.

The extended schema is useful here because it describes the execution wrapper
as well as the underlying value. Current reference requests use this shape:

```json
{
  "href": "https://example.test/input.geojson",
  "type": "application/json"
}
```

An inline complex value may require a wrapper such as:

```json
{
  "value": {
    "type": "FeatureCollection",
    "features": []
  }
}
```

The client should model the transport choice separately from the data format:
inline versus reference, UTF-8 versus base64, and GeoJSON versus GML are
different decisions. It should serialize the exact advertised wrapper rather
than guessing from a filename extension.

### Outputs

The `outputs` object supplies output IDs and value schemas. Together with
`outputTransmission`, this lets the client offer value/reference selection and
format selection where supported. A document response in the current cases is
requested with:

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

Output IDs are just as exact as input IDs. The client should not assume every
process calls its output `Result`, or that a string output is necessarily an
ordinary text value. In the GDAL/OGR processes, a string may actually contain
a server-side path or a download URL.

## Assumptions that are reasonably safe

The following assumptions are safe only after the target server's current
description has been fetched successfully:

- The advertised process, input, and output IDs are the exact identifiers to
  serialize.
- Advertised primitive types and explicit JSON Schema constraints are the
  correct basis for client-side validation.
- Inputs explicitly marked with `minOccurs: 0` may be omitted.
- Advertised defaults can be shown to the user. Omitting an optional input lets
  the server decide whether to apply that default; the client should not claim
  that the default was used until the result confirms it.
- Only advertised job-control and transmission modes should be offered by
  default.
- An advertised media type is a candidate representation, not evidence that an
  arbitrary document with that media type is semantically valid.
- A successful synchronous execution is indicated by the HTTP status and a
  parseable response, not by the status alone.
- An accepted asynchronous execution must be followed through its job resource
  to a terminal state.

Saved requests should be associated with the API origin and a process
description version or hash. Before replay, the client should refresh or
compare the current description and report contract drift.

## Assumptions that are not safe

### Advertised schema does not guarantee executability

`Gdal_Grid` advertises only `OF`, `InputDSN`, and `OutputDSN`. A request using
exactly those inputs passes description-based validation but the provider needs
additional, unadvertised parameters and returns HTTP 500. The client cannot fix
this generically without inventing provider-specific fields. It should retain
the request and response as diagnostics and report a server contract defect.

`Gdal_Dem` provides another example: its advertised fields are insufficient
for the provider's hillshade branch, which requires an unadvertised value. The
verified case uses the advertised `slope` operation instead.

### A broad complex type does not guarantee every geometry

The description can say XML, JSON, or object while the provider parser accepts
only a narrower geometry or document shape. The `Distance` provider rejected
point GML in testing even though its wording is generic; the executable case
uses polygons. Media-type validation alone cannot catch this.

Descriptions may also disagree internally. For example, a title may refer to a
generic "geometry" while a content schema points specifically to a polygon.
The client should show the more specific constraint, warn about conflicting
metadata, and avoid pretending it can resolve the conflict.

### A string is not necessarily portable user text

The GDAL/OGR descriptions expose dataset inputs and outputs as strings. In the
tested provider they are filenames resolved inside the ZOO container, not file
uploads and not generally accessible client paths. The local staging script is
test infrastructure for that deployment; it is not a portable client feature.

The client must not assume that a path on the user's computer is visible to the
server. It should only offer filename/path entry when the deployment explicitly
defines its meaning. Prefer an advertised reference or upload mechanism when
one exists.

### A reference URL may not be reachable by the process server

A URL reachable by the browser or desktop client may be inaccessible from the
server because of DNS, firewall, authentication, TLS, redirect, or container
network differences. Media type and file content can also disagree. A client
may perform advisory checks, but only server-side retrieval proves that the
provider can use the reference.

User-controlled references also have security implications. Deployments should
apply an explicit URL/origin policy to avoid turning the process server into an
unrestricted network fetcher.

### Output strings and links may be malformed

The observed `Ogr2Ogr` response returned a malformed concatenation of two URLs.
The client must parse links defensively and must not automatically navigate to
or fetch an invalid or unexpected URL. Keep the raw value visible so the user
can diagnose the server response.

### Provider errors may be generic or misleading

Observed execution failures use a generic `NoApplicableCode` problem with a
free-text `detail`; one supplies no useful provider message at all. The client
cannot rely on the server to identify a particular input field or consistently
use a 4xx status for bad user data. Invalid input may surface as HTTP 500.

## Handling wrong end-user input

Validation should be layered so the client catches what it knows without
masking what only the provider can decide.

### 1. Validate the request envelope

Before submission, verify that:

- the body is valid JSON and the top-level members have supported shapes;
- `inputs` and `outputs`, when present, are objects;
- every input/output ID exists in the current process description;
- no required input is missing;
- execution, response, format, and transmission choices are advertised;
- an asynchronous request uses the required header, such as
  `Prefer: respond-async`.

Unknown input IDs should produce a clear error or an explicit expert-mode
warning. They should not be silently discarded. An expert override may be
useful for known broken descriptions, but the resulting request must be marked
as outside the advertised contract.

### 2. Validate each value against its advertised schema

Check primitive types without broad implicit coercion. In particular:

- do not turn arbitrary strings into numbers or booleans;
- distinguish integers from floating-point numbers where required;
- preserve `0` and `false`;
- reject `null` unless it is advertised;
- enforce enums, array sizes, and cardinality;
- evaluate `oneOf` branches and ask the user to choose when they are ambiguous;
- validate nested required properties, such as `bbox` and `crs`;
- validate URI syntax where a URI is required.

Defaults should be visually distinguished from values explicitly entered by
the user. This lets the request serializer omit an untouched optional value
instead of changing server behaviour by sending it.

### 3. Validate complex-value metadata and structure

For inline or referenced complex data:

- require the correct wrapper (`value` or `href`);
- require a media type when needed and check it against advertised choices;
- do not confuse `type` on a link with the GeoJSON object's `type` member;
- apply the advertised content encoding;
- parse JSON or XML locally when possible;
- perform format-specific checks, such as GeoJSON object shape, GML geometry
  type, bounding-box dimension, and CRS syntax;
- warn that syntactic validation cannot verify provider compatibility.

Do not automatically rewrite coordinates, CRS identifiers, geometry types, or
axis order. Such transformations are processing decisions and can silently
change the user's data.

### 4. Submit without hiding the server response

On failure, retain and expose:

- HTTP method and final URL;
- response status and headers;
- submitted body, with secrets redacted;
- raw response body;
- parsed problem `title`, `type`, and `detail` where available;
- process ID and description version/hash;
- job ID and last known job state for asynchronous execution.

Map an error to a form field only when the server identifies that field
unambiguously. Otherwise show it as an execution error rather than guessing.
Transport errors, request validation errors, provider failures, job failures,
and response-parse failures should be distinct client states.

### 5. Treat success defensively

For HTTP 200, parse the response according to its actual `Content-Type` and the
requested output contract. Check that expected output IDs exist, but retain
unknown outputs for forward compatibility. A 200 response is not a waiting
job unless it explicitly contains a job resource; the tested synchronous calls
have completed at that point.

For HTTP 201, find the job location in the response or headers, poll the
monitor link, handle `accepted`/`running`/terminal states, and only fetch result
links after success. A job that was accepted can still fail later, as shown by
the `demo` case.

## Recommended internal client model

Keep the raw process description alongside a normalized model. The normalized
model should cover:

```text
Process
├── id, title, description, version
├── execute link and source API origin
├── job-control and output-transmission capabilities
├── inputs[]
│   ├── exact id and display metadata
│   ├── required, nullable, default, cardinality
│   ├── raw schema and normalized alternatives
│   └── literal/complex/bbox and representation choices
└── outputs[]
    ├── exact id and display metadata
    ├── raw schema and normalized alternatives
    └── representation and transmission choices
```

Keeping the raw schema is important for forward compatibility, diagnostics,
and later support for constructs the first form renderer does not understand.
The client should be able to say "this constraint is not supported" rather
than crashing or silently accepting everything.

## Relationship to the generated Postman collection

The implemented collection layout is:

```text
OGC API Processes tests
├── POST_process_sync
│   └── <case folder name>
└── process_descriptions
    └── <process_id>
```

This supports the implementation workflow well:

- each canonical request is available as an executable POST example;
- each represented process has one deduplicated description GET;
- request bodies are copied exactly from `cases/<name>/request.json`;
- asynchronous `Prefer` headers are preserved;
- descriptions and executions can be compared side by side.

Despite its historical name, `POST_process_sync` currently also contains the
asynchronous cases whose headers request `respond-async`. Neither the future
client nor automated analysis should infer execution mode from the folder
name; use the request headers and process capabilities. A future collection
revision could rename it to `POST_process_execution` or split synchronous and
asynchronous requests.

The collection is a generated inspection and test interface, not the client
contract. The source of truth remains each `case.json`, `request.json`, fixture,
captured process description, and observed response.

## Practical implementation priorities

Based on the current evidence, the client should be implemented in this order:

1. Fetch and cache process descriptions per API origin and contract hash.
2. Normalize the common schema features while retaining the raw description.
3. Generate forms for literals, bounding boxes, complex inline values, and
   references.
4. Validate the envelope, identifiers, requiredness, cardinality, and schema
   constraints before submission.
5. Support both synchronous results and the complete asynchronous job lifecycle.
6. Preserve raw requests and responses for useful error reporting.
7. Add explicit handling for description/provider mismatches without embedding
   GDAL-, OGR-, GEOS-, or CGAL-specific assumptions in the generic layer.
8. Run the canonical cases whenever the server profile or description hash
   changes.

