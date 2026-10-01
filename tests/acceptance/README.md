# Service acceptance examples

These constructed HTTP conversations describe services we want the client to
handle. They are not provider captures. Every collected test calls the real
client; the fake transport supplies replies and checks its requests.

```bash
npm test -- tests/acceptance --reporter=verbose
npm run check:local -- tests/acceptance --reporter=verbose
```

There are **14 active acceptance tests**: 12 for pagination/dates and two for
explicit credential headers. They also run in `npm run check` and GitHub Actions.
Eight [prepared auth workflows](pending/) are outside collection until they can
exercise production credential handling. The runner reports this gap; those
drafts contribute no passes, failures or skipped tests to client totals.

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

[authentication.test.ts](authentication.test.ts) has two client tests, one per
credential kind. They call the real client's `send()` with missing, wrong and
correct credentials. Assertions check outgoing URLs and header values, and
preservation of status, problem details and authentication challenges.

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

**Passing these tests establishes explicit request-header handling only.**
The [pending workflows](pending/) cover configuring credentials once for the
whole conversation, later pages, polling, revoked access and external downloads.
Those behaviours are not yet exercised. They are preserved outside collection
instead of reporting hardcoded missing-integration errors as client failures.

API keys in queries/cookies, Basic Auth, OAuth login/refresh, security-scheme
discovery, browser CORS and redirect credential handling are outside these
cases. UI downloads made separately from core need their own tests.

The live [Python gate](../../auth/README.md#api-key-mode) supports both modes.
Use `--auth api-key --api-key-header X-Processing-Key` to match this header name;
configure the client with the gate's chosen key. The gate's own Python checks
run separately and are never counted as client tests.
