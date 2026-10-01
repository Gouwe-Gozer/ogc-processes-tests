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
