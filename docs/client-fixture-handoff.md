# Running the recorded client tests

This repository owns a small cross-provider regression suite as well as the
recordings it uses. Tests import the real `@breinstein/oap-client` package and
supply recorded responses through its existing `FetchLike` interface. ZOO,
pygeoapi, and Weaver are fixture sources for shared client concerns.

The client repository continues to own its implementation and internal unit
tests. This suite can run independently, locally or in GitHub Actions, without
a sibling checkout or a live provider.

## Run locally and in CI

Use Node 24 or later:

```bash
npm ci
npm run check
```

`check` runs TypeScript checking and Vitest. `npm test` runs just the tests.
Dependencies, including client version `0.3.2`, are pinned in
[`package.json`](../package.json) and [`package-lock.json`](../package-lock.json).
Installation requires access to npm; the tests do not require network access.
[`tests/setup.ts`](../tests/setup.ts) blocks ambient `fetch` and fails even when
the client catches that blocked call.

The [GitHub Actions workflow](../.github/workflows/test.yml) runs the same two
commands on pushes, pull requests, and manual dispatch. It needs no provider
containers, service credentials, or separate client checkout. Live tests and
browser CORS checks remain a separate future concern.

To test a reviewed client release, update the exact dependency and lockfile,
then run the suite and inspect changed behaviour before committing the update.
The default CI job tests the pinned release, not the latest client source.

The installed 0.3.2 package was inspected on 25 September 2026. It also exports
job status, polling, results retrieval, dismissal and job listing functions.
The original 16 tests pass against this release; lifecycle coverage is the next
addition. The source links below document the original integration baseline.

## Implemented client boundary

The initial integration is based on client source commit `48ee066`, package
version `0.2.0`, inspected on 17 September 2026. It has a public API, response
and error types, and an injectable fetch:

```ts
type FetchLike = (input: string, init?: RequestInit) => Promise<Response>;
```

The suite imports that type from the client. The
[public entry point](https://github.com/ITBreinstein/oap-client/blob/48ee066/packages/core/src/index.ts#L8)
exports `createClient`, `execute`, `getProcess`, `parseDescription`,
`ProcessesError`, and the HTTP/envelope functions. The
[fetch contract](https://github.com/ITBreinstein/oap-client/blob/48ee066/packages/core/src/http/fetch.ts#L6)
is already implemented; the test double does not introduce a new transport API.

[`recorded-fetch.ts`](../tests/support/recorded-fetch.ts) has two small operations:

- `readExchange(scenario, step, variables)` loads an existing request/response
  pair. Tests explicitly name the files they need.
- `recordedFetch(...exchanges)` returns an injected fetch, captured calls, and
  `assertDone()`. It checks the next recorded method and URL, then returns a
  fresh native `Response`. Unexpected requests fail; there is no live fallback.
  Tests call `assertDone()` to detect unused exchanges and extra attempts,
  including request mismatches caught by the client.

The real client handles envelopes, protocol parsing, execution classification,
and errors. Tests assert outgoing headers/bodies and public outcomes directly.
The helper does not poll, select renderers, normalize provider payloads, or
implement client behaviour. Its local capture types describe existing on-disk
metadata, not a new scenario specification or replacement client models.

## Initial coverage

| Client concern | Existing scenarios | Executable tests |
|---|---|---|
| Discovery and listing | `protocol/discovery/weaver-redoak/core-discovery` | [discovery.test.ts](../tests/protocol/discovery.test.ts) |
| Description/schema preservation | pygeoapi raw-versus-document description; `protocol/discovery/weaver-local/process-description` | [descriptions.test.ts](../tests/protocol/descriptions.test.ts) |
| Synchronous execution and body preservation | ZOO `simple-sync`; pygeoapi `raw-versus-document-response`; Weaver `sync-with-job-links` | [execution.test.ts](../tests/protocol/execution.test.ts) |
| Structured and HTML HTTP errors | ZOO `structured-execution-error` and `process-description-html-error` | [errors.test.ts](../tests/protocol/errors.test.ts) |
| Accepted submission and job location | First exchange of ZOO and Weaver `successful-job` | [submission.test.ts](../tests/protocol/submission.test.ts) |

The scenario READMEs retain their links to provider evidence. Selection follows
implemented client behaviour, not a provider-specific test framework. A scenario
can serve another concern later without being copied.

The [helper tests](../tests/support/recorded-fetch.test.ts) check that a bad
request cannot silently pass, responses have independent readable bodies, URLs
are preserved, and `body_file` can supply original bytes. Their controlled
variations are loader checks, not additional provider evidence. Reading the
large CSV verifies byte loading, not table rendering or download UI behaviour.

## Capture conversion and limits

- The outer `status`, `headers`, `final_url`, and `body` fields are capture
  metadata. A description parser receives only `body`, with the resolved
  `final_url` as `documentUrl`.
- The test fetch preserves response status and headers. Objects, arrays,
  numbers, booleans, and null are JSON-serialized; stored strings are returned
  as raw text. The selected string bodies are HTML error pages. A JSON string
  scalar is ambiguous in this capture format: preserve its original wire
  bytes in a body file before adding such a test, rather than guessing.
- Known placeholders are expanded consistently in request and response files,
  including headers and bodies. Tests supply fixed job IDs/URLs. Missing
  variables fail the test. Existing absolute links and query parameters are
  retained, even when they name a real host; all requests are intercepted.
- The requested URL and `final_url` stay separate. The test sets the native
  response's `url`, which otherwise starts empty; the client constructs its
  own envelope. The helper's redirect check is controlled test data, not a
  claim that the selected providers redirected.
- `body_file` is resolved relative to its response JSON file and read as bytes.
  It is distinct from an API output's `href`. The large CSV stays under
  `evidence/` and is not duplicated.
- JSON serialization and placeholder substitution do not reproduce original
  wire bytes. Recorded headers remain evidence; tests must not compare stored
  `Content-Length` with the size of reserialized JSON. Use original body files
  when byte lengths or encodings matter.

Recorded requests are not automatically exact expectations for the current
client. Weaver's sync capture sends `Prefer: wait=30` and body `mode: "sync"`.
The client's execute API sends `Accept: */*`, no sync `Prefer`, and only
`inputs`, `outputs`, and `response` in the body; see
[buildHeaders](https://github.com/ITBreinstein/oap-client/blob/48ee066/packages/core/src/execution/build-request.ts#L115)
and [buildPayload](https://github.com/ITBreinstein/oap-client/blob/48ee066/packages/core/src/execution/build-request.ts#L216).
Tests make these differences explicit in their assertions. The helper does not
rewrite requests or enforce every recorded header. Passing offline tests proves
handling of the selected responses, not that a provider would accept a changed
request live. Replayed headers also do not reproduce browser CORS filtering.

## Extending the suite

Add ordinary tests under `tests/` using an existing representative scenario
where possible. Import only the published client's public API. Keep expected
behaviour in the test assertions, with explanatory context in the scenario
README; do not introduce `testcase.json` or expectation manifests. Add captures
only for distinct behaviour or a demonstrated evidence gap, preserving provider
provenance.

Job status, polling, dismissal and result retrieval now have public interfaces
in 0.3.2; recorded lifecycle tests can use them. Execution callbacks still wait
for client support. Form generation and semantic
map/table/value/download selection also remain pending. Submission tests stop
at the returned job handle, and schema-preservation tests do not imply that
forms or result renderers exist. Broader controlled HTTP tests belong beside
the client's HTTP implementation; only the fixture loader needs its own small
support checks here.
