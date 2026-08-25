# Error and warning catalogue

[`error.catalog.json`](error.catalog.json) is the machine-readable catalogue of
every distinct execution or terminal-job error message currently captured for
the 44 core processes. It preserves the exact server text, groups identical
messages across cases, and records the context needed to use the message
safely.

| Distinct message | Observed context | Useful client treatment |
|---|---|---|
| `... signal 11 = SIGSEGV` | HTTP 500 from five SAGA case shapes | Identify a server-side process crash; show the raw detail |
| `... signal 6 = SIGABRT` | HTTP 500 from two SAGA case shapes | Identify a server-side process abort; show the raw detail |
| `... No message provided` | HTTP 500 from `Gdal_Grid` | Say the server supplied no actionable diagnostic detail |
| `... Failed running from R world!` | HTTP 500 from `failR` | Show the provider detail without assigning it to an input |
| `... Error executing the service` | terminal `failed` async `demo` job | Show job failure after an accepted submission |

Identical text is grouped, but every occurrence remains linked to its case and
raw evidence file. This matters because `SIGSEGV`, for example, occurs for
different raster, interpolation, and point-cloud request shapes and therefore
does not establish one root cause.

Future distinct messages should be added to `error.catalog.json`; repeated
occurrences of an existing message should extend that entry's `cases` list and
retain their individual raw response evidence.

## Safeguard boundary

The catalogue can support consistent presentation and cautious hints:

- retain HTTP status, response headers, final URL, parsed problem fields, and
  raw body;
- distinguish a failed HTTP execution from a successfully accepted async job
  that later reaches terminal status `failed`;
- label operating-system signals as server/provider crashes;
- show provider text verbatim and allow the request to be inspected;
- avoid assigning blame to an input unless the server identifies it;
- avoid automatic retries solely because a known message was recognized.

Some defective results carry no error message. The machine-readable catalogue
therefore also records silent HTTP-200 anomalies: missing requested outputs and
an unusable output reference. For those, a client can warn that the response is
incomplete or the referenced result cannot be retrieved, while still retaining
the nominal HTTP status and raw result.
