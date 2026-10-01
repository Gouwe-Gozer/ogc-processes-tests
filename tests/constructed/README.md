# Constructed client conversations

These tests give the real OAP client a deliberately written conversation with
an imaginary service. They use the same fake transport as our recorded tests.
No API server or processing algorithm runs. The client itself discovers links,
retrieves pages, builds the execution request, polls and reads the result.

The JSON responses are written directly in
[pagination-workflow.test.ts](pagination-workflow.test.ts) and
[access-failures.test.ts](access-failures.test.ts). They are constructed
test data, not observations about ZOO, Weaver, pygeoapi or another provider.
Real provider exchanges remain in `evidence/` and `scenarios/`.

## Pagination workflow

| Test | Conversation and checks |
|---|---|
| Complete workflow | Discover a catalogue; read three pages; select the process found only on page three; read its description; submit it; see running then successful status; retrieve its result. Check the complete list, request body and headers, job outcome, result body and exact request order. |
| Page two fails | Repeat discovery and page one, then return HTTP 503 with a problem document. Check that listing rejects with the failed page's URL, status and explanation, rather than returning page one as a complete catalogue. No later request is permitted. |

The pages advertise relative links and opaque cursor values. Description,
execution, status and results use distinct advertised addresses. The client
must follow those links; assuming standard paths or calculating page numbers
would fail the test. Ten requests complete the successful conversation; four
reach the second-page error. The transport rejects extra or out-of-order calls.

OAP already has unit tests for pagination loops, page caps, duplicates,
cancellation and malformed documents, plus two captured ZOO catalogue pages.
These tests exercise several public client operations together through one
`createClient` instance. They complement those focused unit tests.

## Access failures

Four tests in [access-failures.test.ts](access-failures.test.ts) check what
happens when the service refuses access during a conversation:

| Test | What the real client must do |
|---|---|
| Catalogue page two returns 401 | Reject listing instead of returning page one as complete. Keep the failed URL, problem details and `WWW-Authenticate` challenge available. |
| Execution returns 403 | Reject the execution with the service's explanation. Send the execution POST once and make no status request. |
| Polling returns 401 | Submit successfully, observe a running job, then stop polling on the refusal. Preserve the challenge and error details; keep the last observed job state as running. Do not resubmit, dismiss or fetch results. |
| Results return 403 | Submit successfully and poll to successful status, then follow the advertised results URL and report its refusal. Keep the successful job status. Do not retry execution or guess another results URL. |

Each test asserts the exact requests made as well as the public error. All
refusals use `application/problem+json`. The two 401 cases include a Bearer
challenge header. These are prepared responses: no token is issued, checked,
expired or refreshed. They test **handling access failures**, not successful
authentication or which credentials a server accepts. No secrets are needed.

The client checkout at `683b7bb` has separate browser-to-relay session handling;
the relay excludes authorization and cookies when forwarding to the service.
That session token does not authenticate a user to an OGC service. Successful
service login, token refresh, cookie behaviour and relay routing need tests
using the client's corresponding implementation. This suite imports the core
package and does not load the web app or relay.

## Try it

From the repository root, after installing dependencies:

```bash
npm test -- tests/constructed/pagination-workflow.test.ts --reporter=verbose
```

To run just the access-failure tests:

```bash
npm test -- tests/constructed/access-failures.test.ts --reporter=verbose
```

To run all eight constructed tests against the sibling client source:

```bash
npm run check:local -- tests/constructed --reporter=verbose
```

All eight tests are also included in `npm run check` and the existing GitHub Actions
workflow. The polling cases use a short polling interval; they do not test
timing precision or replace the client's polling loop.

These checks do not establish live-server compatibility or browser behaviour.
These cases do not cover successful service-wide authentication. Separate
[acceptance cases](../acceptance/) cover job pagination, date queries and explicit
credential headers. Eight protected workflows remain prepared outside the
collected tests until production client credentials can be configured.
Browser enforcement of access to `WWW-Authenticate` is also outside these core tests; the fake transport makes response headers readable.

## Response handling

Two cases in [response-envelope.test.ts](response-envelope.test.ts) call the
real client's `send()` operation. They check that requested and final response
URLs stay distinct, and that successive requests return independent, readable
results. The replies are constructed, including redirect metadata; no live
redirect is followed. These replace helper-only checks of response construction.
