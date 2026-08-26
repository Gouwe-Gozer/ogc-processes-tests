# OGC API Processes client core

The client core is the part of the library that understands OGC API -
Processes. It should support:

- the landing page and its links;
- `/conformance`;
- the process list and process descriptions;
- synchronous execution;
- asynchronous jobs, status, results, and dismissal.

Forms, maps, and result viewers use the core, but are not part of it. If the
core does not understand part of a process schema, it returns the original JSON
so the application can offer a raw JSON editor.

## HTTP transport

The core should not call browser `fetch` directly. It should call a small HTTP
interface. This makes it possible to add a relay later if a server cannot be
called directly from a browser.

The interface only needs:

- `GET`, `POST`, and `DELETE`;
- a URL and headers;
- an optional request body;
- an optional `AbortSignal`;
- the response status, headers, final URL, and raw body.

For example:

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

An HTTP 400 or 500 response is still a response. The transport should return it
to the core so the core can read the error body. It should only throw when no
HTTP response was received or the request was aborted.

The existing `examples/ogc-client` project has useful examples of typed errors,
link resolution, and separate tests for network, HTTP, parsing, and abort
errors. Its cache, request deduplication, global fetch settings, and XML focus
are not needed here. Keep its BSD-3-Clause notice if code is copied from it.

## Discovery

Start with the configured API URL. Read the landing page and follow its links
to conformance and processes. Resolve relative links against the final URL of
the response that contained them.

Fetch each process description separately. If one description fails, keep the
other processes available. Store both:

- the original description JSON;
- the fields the client understands and uses.

Unknown fields or unsupported schema types should not make the whole process
list fail.

## Execution

The core should support:

- synchronous raw and document responses;
- asynchronous requests using `Prefer: respond-async`;
- output by value or reference when the process advertises it.

HTTP 200 usually means a synchronous result is in the response. HTTP 201 means
an asynchronous job was accepted. It does not mean that the job succeeded.

Use the same result parser for synchronous results and
`/jobs/{jobID}/results`. Keep unknown output IDs and the original response.
Rendering GeoJSON, GML, rasters, tables, or other values belongs in the
application.

## Asynchronous jobs

For an accepted job:

1. Read the `Location` header without assuming header-name capitalization.
2. If `Location` is missing, a monitor link in the body can be used as a
   fallback.
3. Resolve relative job and result links against the response URL.
4. Treat `accepted` and `running` as unfinished.
5. Treat `successful`, `failed`, and `dismissed` as finished.
6. Fetch results only after the job is `successful`.
7. Send `DELETE` to dismiss a job when dismissal is supported.

Stopping a browser request with `AbortSignal` does not dismiss the server job.

A small “poll until finished” helper is useful. Persistent background polling,
automatic retries, and job history are not required.

## Not part of the core

Do not add these unless the tender or a real test server requires them:

- an OAuth framework;
- automatic retries;
- proxy or TLS configuration;
- a cache system;
- permanent download storage;
- request history or monitoring systems;
- fixes for individual providers.

Applications can still supply custom headers. A relay can still be added as a
second implementation of the small transport interface.

## Suggested implementation order

1. HTTP interface and browser `fetch` implementation.
2. Landing-page links and conformance.
3. Process list and descriptions.
4. Supported schema fields plus raw JSON fallback.
5. Synchronous execution and results.
6. Asynchronous submission, status, results, and dismissal.
7. Tests using the representative exchanges in [`../examples/`](../examples/).
