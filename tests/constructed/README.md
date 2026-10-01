# Constructed client conversations

These tests give the real OAP client a deliberately written conversation with
an imaginary service. They use the same fake transport as our recorded tests.
No API server or processing algorithm runs. The client itself discovers links,
retrieves pages, builds the execution request, polls and reads the result.

The JSON responses are written directly in
[pagination-workflow.test.ts](pagination-workflow.test.ts). They are constructed
test data, not observations about ZOO, Weaver, pygeoapi or another provider.
Real provider exchanges remain in `evidence/` and `scenarios/`.

## What the two tests do

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

## Try it

From the repository root, after installing dependencies:

```bash
npm test -- tests/constructed/pagination-workflow.test.ts --reporter=verbose
```

To run the same tests against the sibling client source:

```bash
npm run check:local -- tests/constructed/pagination-workflow.test.ts --reporter=verbose
```

Both tests are also included in `npm run check` and the existing GitHub Actions
workflow. They use the normal short polling interval; they do not test timing
precision or replace the client's polling loop.

These checks do not establish live-server compatibility or browser behaviour.
They do not cover paginated job lists, date filtering or authentication. Those
need separate cases tied to the corresponding client functionality.
