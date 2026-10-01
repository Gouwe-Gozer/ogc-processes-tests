# Service acceptance examples

These deliberately constructed HTTP conversations describe services we want
the client to handle. They are not captures from a provider and do not describe
how OAP is implemented. The real client receives the replies through the
existing fake transport; no processing server or replacement client runs.

Run them against the pinned npm client or the sibling source:

```bash
npm test -- tests/acceptance --reporter=verbose
npm run check:local -- tests/acceptance --reporter=verbose
```

They also run in `npm run check` and GitHub Actions. Failures remain failures:
requirements are not weakened or marked as expected failures to keep CI green.
On 1 October 2026, both npm 0.3.2 and local core 0.5.0 (commit `683b7bb`)
reported **14 passing acceptance cases and eight integration failures**.
Type checking passed. The full suite reported **45 passed and eight failed**.

## Pagination and dates

[pagination-and-dates.test.ts](pagination-and-dates.test.ts) has 12 cases:

- Job discovery, multiple pages and an empty final page.
- Process and job next links supplied through HTTP headers.
- A failed later job page, with no silent partial success.
- Job date filters: an instant, a closed interval, either open end and a
  positive timezone offset; a filtered cursor leads to the next page.
- An empty filtered selection and an invalid-date service refusal.
- Date and date-time inputs preserved in an execution request.

These examples follow [OGC API Processes Part 1](https://docs.ogc.org/is/18-062r2/18-062r2.html):
section 7.7 describes pagination, section 7.8 describes HTTP Link headers,
and section 11.2.5 defines the job `datetime` parameter. A next link may use an
opaque cursor that carries the selection without repeating the date parameter.

The date-listing cases supply a URL to OAP's exported `listJobs(url)`.
They check preservation of the query, navigation and returned jobs. They do
not prove that the UI can offer a date picker or that `client.listJobs()`
accepts a separate date option. The service replies already represent the
selected jobs; these tests do not implement or validate a server's filtering
algorithm. The process-input case separately checks outgoing JSON values.

The examples do not simulate a browser, CORS, redirects or a live provider.
The existing three-page process-to-result conversation remains in
[constructed/pagination-workflow.test.ts](../constructed/pagination-workflow.test.ts).

## Bearer tokens and API keys

[authentication.test.ts](authentication.test.ts) adds ten cases, five for each
credential kind. All credentials are deliberately public test values.

| Requirement | Current result |
| --- | --- |
| An explicit header on one OAP `send()` request is transmitted; missing and wrong values are refused | Two passing tests |
| Configure a credential once, then discover, follow pages, submit, poll and download CSV | Two integration failures |
| Follow a result on another origin without sending the service credential there | Two integration failures |
| A wrong configured credential preserves the service refusal and stops discovery | Two integration failures |
| Revoked access during polling preserves the explanation without repeating execution | Two integration failures |

Bearer uses the `Authorization` header as described in
[RFC 6750 sections 2.1 and 3](https://www.rfc-editor.org/rfc/rfc6750.html#section-2.1).
The API-key example requires `X-Processing-Key`; the name is part of the example
service's contract. [OpenAPI security schemes](https://spec.openapis.org/oas/v3.0.3#security-scheme-object)
allow services to choose their key header name. This example returns 403 for
missing or wrong API keys; that status is a fixture choice, not a universal
API-key rule. Bearer refusals use 401 with a challenge.

`protected-conversation.ts` acts as the service at the existing fake-fetch
boundary. It checks the header before releasing the next reply. It never
inserts headers, repairs URLs, calculates page numbers or filters jobs.
No socket, extra API server, Docker container or real credential is needed.

### The one connection still needed

`oap-auth-binding.ts` is the small connection to OAP's **production** credential
handling. It currently raises `AUTH_INTEGRATION_MISSING`, before making an
authenticated request. The core offers injected fetch and per-request headers,
but this suite has no client-owned service-credential implementation to call.
The two passing `send()` checks must not be presented as working authentication
through OAP's high-level operations or web app.

The eight workflow cases contain their conversations and assertions already.
Connect the real implementation in that one file when available; keep the
service rules unchanged. It may belong to a client-owned fetch implementation
rather than to core itself. We do not invent an `auth` option or supply our own
auth wrapper to make the cases pass. A newer client checkout will still report
this integration gap until that connection is made. These failures do not yet
prove a defect in requests sent by OAP: those workflow assertions have not run.

Once connected, a failure from the service or an assertion identifies the
operation that did not meet the example's requirement. Missing/wrong credentials
are rejected, valid credentials must survive every protected step, and the
cross-origin result must receive no service credential. The existing fake
transport also rejects extra, missing or out-of-order requests.

API keys in query strings or cookies, Basic Auth, OAuth login/refresh, automatic
security-scheme discovery, browser CORS and redirect credential handling are
outside these cases. The external-result test covers an advertised link, not
an HTTP redirect. UI downloads made separately from core need their own tests.
The live [Python gate](../../auth/README.md#api-key-mode) also supports both
modes. Use `--auth api-key --api-key-header X-Processing-Key` to match the
header name in these examples; configure the client with the gate's chosen
key value. Gate checks remain separate from OAP's auth implementation.
