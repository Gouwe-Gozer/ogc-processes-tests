# Service acceptance examples

These constructed HTTP conversations describe services we want the client to
handle. They are not provider captures. Every collected test calls the real
client; the fake transport supplies replies and checks its requests.

```bash
npm test -- tests/acceptance --reporter=verbose
npm run check:local -- tests/acceptance --reporter=verbose
```

There are **22 active acceptance tests**: 12 for pagination/dates and ten for
authentication. All run in `npm run check`, `npm run check:local` and the normal
GitHub Actions client job. Unsupported behaviour stays visible as a failure;
there are no pending auth files or unconditional missing-integration errors.

## Pagination and dates

[pagination-and-dates.test.ts](pagination-and-dates.test.ts) covers job discovery,
multiple pages, an empty final page, HTTP next links for jobs and processes,
and a failed later job page. Date cases cover an instant, closed interval,
either open end, a positive timezone offset, an empty selection, an invalid-date
refusal and date values in execution inputs.

These examples follow [OGC API Processes Part 1](https://docs.ogc.org/is/18-062r2/18-062r2.html):
sections 7.7 and 7.8 describe pagination and HTTP Link headers; section 11.2.5
defines job `datetime`. An opaque next cursor may carry the selection without
repeating the date parameter.

The date-listing cases supply a URL to OAP's exported `listJobs(url)`. They check
query preservation, navigation and returned jobs. They do not prove that the
UI offers a date picker or that `client.listJobs()` accepts a separate date
option. Replies already contain selected jobs; these tests do not validate a
server's filtering algorithm. The process-input case checks outgoing JSON.

## Bearer tokens and API keys

[authentication.test.ts](authentication.test.ts) runs five cases for each
credential kind:

| Client operation | Expected behaviour |
|---|---|
| `client.send()` with missing, wrong and correct credentials | Preserve both refusals and accept the protected reply only when the correct header is sent. |
| `client.listProcesses()` without credentials | Report the protected landing page's refusal and stop, without guessing another catalogue URL. |
| Exported core `execute()` without credentials | Report the protected execution's refusal without repeating the POST or starting a job. |
| `client.pollJob()` without credentials | Report the refusal, stop polling, and make no execution or results request. |
| `client.getResults()` without credentials | Follow the advertised CSV link and report its refusal rather than returning the error body as a successful download. |

All cases call real OAP code. They check outgoing requests, response status,
problem details and the Bearer challenge. The standalone `execute()` entry point
uses an already-known process collection, so a discovery failure cannot prevent
the submission check from reaching its protected endpoint.

On 1 October 2026, both npm **0.3.2** and local core **0.5.0** at `a68ff6a`
passed eight auth tests and failed the two discovery cases. The client requests
`/api/`, receives 401 or 403, then requests `/api/processes` without credentials.
Our acceptance requirement is to stop at that authentication refusal. This is
an explicit suite requirement, not a claim that OGC forbids every discovery
fallback. The tests remain ordinary failures, not skipped or expected-failure
cases. Across the full suite, the result is **48 passed, two failed**; both
commands exit unsuccessfully until that behaviour changes.

Run only the auth cases with:

```bash
npm test -- tests/acceptance/authentication.test.ts --reporter=verbose
npm run check:local -- tests/acceptance/authentication.test.ts --reporter=verbose
```

Bearer uses `Authorization` as described in
[RFC 6750 sections 2.1 and 3](https://www.rfc-editor.org/rfc/rfc6750.html#section-2.1).
The API-key example requires `X-Processing-Key`; that name is the example
service's contract. [OpenAPI security schemes](https://spec.openapis.org/oas/v3.0.3#security-scheme-object)
allow a service to choose its key header. The example returns 403 for missing
or wrong keys; this is a fixture choice, not a universal API-key rule. Bearer
refusals use 401 with a challenge. All secrets are public test data.

`protected-conversation.ts` acts as the service at the fake-fetch boundary.
It checks credentials before releasing replies and never inserts headers on
the client's behalf. No extra API server, Docker or real secret is needed.

**These tests cover explicit credential headers and client reactions to a
protected service. They do not establish automatic credential management.**
OAP's current core accepts headers on `send()` but has no service-credential
setting for its higher-level operations. The tests do not invent one, wrap the
client's fetch to add credentials, or refresh tokens for it.

The old eight workflow drafts threw `AUTH_INTEGRATION_MISSING` before any
request. They have been replaced by the eight runnable operation checks above;
this restores client auth coverage without claiming that the original complete
authenticated workflows are implemented. Their remaining requirements are:

- Configure credentials once for discovery, pagination, descriptions, execution,
  polling and a protected CSV result.
- Follow an external result link without sending the service credential there.
- Report wrong configured credentials and revoked access during polling without
  resubmitting the calculation.

Those successful-flow and credential-scoping requirements need calls to a real
client credential API when one exists. They are documented here rather than
represented by a helper that always throws or implements authentication itself.

API keys in queries/cookies, Basic Auth, OAuth login/refresh, security-scheme
discovery, browser CORS and redirect credential handling are outside these
cases. UI downloads made separately from core need their own tests.

The live [Python gate](../../auth/README.md#api-key-mode) supports both modes.
Use `--auth api-key --api-key-header X-Processing-Key` to match this header name;
configure the client with the gate's chosen key. The gate's own Python checks
run separately and are never counted as client tests.
