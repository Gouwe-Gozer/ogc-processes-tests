# Using these fixtures in the client

The client can already consume selected recordings through its existing tests.
Keep the recordings here and put executable assertions beside the client code.
This guide supplies a small example to copy into that suite; it does not add a
test runner or a replay framework to this repository.

## Inspected client

This guide targets `oap-client` commit `48ee066`, package version `0.2.0`,
inspected on 17 September 2026. Its public API, HTTP boundary, and Vitest runner
are implemented. Pin both repositories to reviewed commits when adopting the
example, and review the client API again when updating that pin.

| Existing public API | What the recordings can test now |
|---|---|
| `parseDescription(body, { documentUrl })` | Input/output IDs, cardinality, and preservation of the original schemas |
| `createEnvelope(response, { requestedUrl })`, `classify`, `requireOk` | Response metadata, readable bodies, structured problems, and non-JSON HTTP errors |
| `gatherEvidence`, `classifyExecution` | Immediate result versus accepted job, and the route to the job status URL |
| `execute`, `createClient` | Execution requests and returned outcomes using the client's injected `fetch` |

These are exported through the client's
[public entry point](https://github.com/ITBreinstein/oap-client/blob/48ee066/packages/core/src/index.ts#L8).
The HTTP injection contract is
[`FetchLike`](https://github.com/ITBreinstein/oap-client/blob/48ee066/packages/core/src/http/fetch.ts#L6):
`(input: string, init?: RequestInit) => Promise<Response>`. Return a native
`Response` from a test fetch and let the real client construct its envelope.
Use the client's own exported types instead of defining replacement client
models here.

The client uses Vitest, with Node for core tests. It already has both MSW
handlers and small injected fetch functions; see its
[test configuration](https://github.com/ITBreinstein/oap-client/blob/48ee066/vitest.config.ts#L9)
and [execution tests](https://github.com/ITBreinstein/oap-client/blob/48ee066/packages/core/test/execution/execute.test.ts#L25).
The example below exercises exported response-handling functions without any
HTTP requests.

Job polling, status methods, dismissal, callbacks, and result-retrieval helpers
are not implemented in this client version. Form generation and semantic result
selection (map, table, ordinary value/JSON, or download) are also pending.
`classifyExecution` distinguishes an immediate result from a job; it does not
unwrap or choose a presentation for the result.

## Converting a capture at the test boundary

- The outer `status`, `headers`, `final_url`, and `body` fields describe the
  recorded HTTP exchange. Pass only `body` to a process-description parser.
  Supply the resolved `final_url` as its `documentUrl`.
- For an HTTP response, preserve status and headers. Serialize a parsed JSON
  body as JSON; use recorded text directly for HTML or CSV. Do not JSON-quote
  an HTML error page. A JSON string payload, if encountered, needs JSON
  serialization rather than the text-body rule.
- Resolve known placeholders consistently in URLs, header values, and bodies.
  Offline tests assign fixed job IDs and URLs; live flows obtain them from the
  server. Preserve existing absolute links and query parameters. Fail on an
  unresolved placeholder instead of silently making up a URL.
- Keep the requested URL separate from the final response URL. A constructed
  `Response` has an empty `url`; set that property in the test before calling
  `createEnvelope`, which otherwise falls back to the requested URL. Do not
  replace the requested URL with the final URL to simulate a redirect.
- A `body_file` path is relative to the response JSON file. Read that file as
  bytes when using the [large CSV scenario](../scenarios/results/downloads/directed-local/large-raw-csv/).
  It is not an API output reference. The example below uses only inline JSON.
- Parsed JSON and placeholder substitution do not reproduce the original wire
  bytes. Keep recorded headers as evidence, but do not assert that the stored
  `Content-Length` equals a reserialized body's size. Use original body files
  for tests that depend on byte lengths or encodings.

Recorded requests are evidence of what a provider accepted, not automatically
exact expectations for the client's request builder. For example, the Weaver
sync request includes `Prefer: wait=30` and body `mode: "sync"`. The current
client sends `Accept: */*`, no sync `Prefer`, and only `inputs`, `outputs`, and
`response` in the body; see
[buildHeaders](https://github.com/ITBreinstein/oap-client/blob/48ee066/packages/core/src/execution/build-request.ts#L115)
and [buildPayload](https://github.com/ITBreinstein/oap-client/blob/48ee066/packages/core/src/execution/build-request.ts#L216).
Document such differences rather than changing captures or adding provider
adapters. A response-only test does not prove the client can reproduce the
original exchange against a live server.

## First handoff: two Weaver responses

Use these existing captures without copying or converting them into another
fixture format:

| Capture | Regression covered |
|---|---|
| [Synchronous result with job links](../scenarios/protocol/execution/weaver-local/sync-with-job-links/01-execute.response.json) | HTTP 200 is immediate despite job-related links and `Content-Location`; preserve the body and metadata |
| [Accepted submission](../scenarios/protocol/jobs/weaver-local/successful-job/01-submit.response.json) | HTTP 201 produces a job handle through `Location` even though the body has no monitor links |

The adjacent scenario READMEs link to the original provider evidence. Only the
submission from the successful-job scenario is used here; its later polling
and results records remain available for the future lifecycle tests.

Place the following example at
`oap-client/packages/core/test/execution/weaver-recordings.test.ts`. It assumes
the two repositories are sibling checkouts. The relative fixture URL is the
only checkout-layout assumption; change it if the client team stores the
fixture checkout elsewhere. It imports the public source entry point, as the
client's own tests do; an external package consumer would import these names
from `@breinstein/oap-client`. JSON is loaded dynamically so the external
captures do not need to be added to the core TypeScript project. No client
configuration change is needed.

```ts
import { expect, it } from "vitest";
import {
  classifyExecution,
  createEnvelope,
  gatherEvidence,
  requireOk,
} from "../../src/index.js";

const scenarios = new URL("../../../../../ogc-processes-tests/scenarios/", import.meta.url);
const baseUrl = "https://weaver.test";
// Both recorded requests target this URL, independently of their final_url.
const requestedUrl = `${baseUrl}/processes/EchoProcess/execution`;
const syncJobUrl = `${baseUrl}/processes/EchoProcess/jobs/sync-1`;
const jobUrl = `${baseUrl}/processes/EchoProcess/jobs/async-1`;
const variables: Readonly<Record<string, string>> = {
  baseUrl,
  syncJobId: "sync-1",
  syncJobUrl,
  jobId: "async-1",
  jobUrl,
};

// Local to these two inline-JSON captures, not a general scenario loader.
async function readResponse(path: string) {
  const fixture = (await import(new URL(path, scenarios).href, { with: { type: "json" } })) as {
    default: unknown;
  };
  const source = JSON.stringify(fixture.default);
  const expanded = source.replace(/\{\{([^{}]+)\}\}/g, (_token, name: string) => {
    const value = variables[name];
    if (value === undefined) throw new Error(`Unresolved fixture variable: ${name}`);
    return JSON.stringify(value).slice(1, -1);
  });
  const capture = JSON.parse(expanded) as {
    status: number;
    headers: Record<string, string>;
    final_url: string;
    body: unknown;
  };
  const response = new Response(JSON.stringify(capture.body), {
    status: capture.status,
    headers: capture.headers,
  });
  Object.defineProperty(response, "url", { value: capture.final_url });
  return { capture, envelope: createEnvelope(response, { requestedUrl }) };
}

it("preserves Weaver's immediate result despite its job links", async () => {
  const { capture, envelope } = await readResponse(
    "protocol/execution/weaver-local/sync-with-job-links/01-execute.response.json",
  );
  await requireOk(envelope);
  const result = classifyExecution(envelope, await gatherEvidence(envelope), "sync");

  expect(result.kind).toBe("immediate");
  if (result.kind !== "immediate") throw new Error("Expected an immediate result");
  expect(result.requestedMode).toBe("sync");
  expect(result.response.status).toBe(200);
  expect(result.response.requestedUrl).toBe(requestedUrl);
  expect(result.response.url).toBe(capture.final_url);
  expect(result.response.headers.get("content-location")).toBe(`${syncJobUrl}/results`);
  expect(result.response.links).toEqual(
    expect.arrayContaining([expect.objectContaining({ rel: "monitor", href: syncJobUrl })]),
  );
  expect(await result.response.json()).toEqual(capture.body);
});

it("locates Weaver's accepted job through Location without body links", async () => {
  const { capture, envelope } = await readResponse(
    "protocol/jobs/weaver-local/successful-job/01-submit.response.json",
  );
  await requireOk(envelope);
  const result = classifyExecution(envelope, await gatherEvidence(envelope), "async");

  expect(envelope.status).toBe(201);
  expect(capture.body).not.toHaveProperty("links");
  expect(result.kind).toBe("job");
  if (result.kind !== "job") throw new Error("Expected a job handle");
  expect(result.requestedMode).toBe("async");
  expect(result.job.statusUrl).toBe(jobUrl);
  expect(result.job.jobId).toBe("async-1");
  expect(result.job.discoveredVia).toBe("location-header");
  expect(result.job.links).toEqual([]);
});
```

From an installed client checkout, run its existing core test project:

```bash
pnpm exec vitest run --project core packages/core/test/execution/weaver-recordings.test.ts
```

No provider needs to be running, and no output links are fetched. This tests
the real response-handling code and preserves the returned payload; it does
not test request construction, polling, CORS, or result rendering. Those
concerns can use the same recordings when their client interfaces are ready.

Keep assertions in the client suite after adoption. This repository continues
to own the captures, provenance, and explanatory notes, without an additional
machine-readable description of expected behaviour.
