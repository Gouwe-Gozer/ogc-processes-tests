# Local BGT prototype

This deployment points to the unfinished local `bgt-land-cover-summary`
process captured on 2026-08-25. It runs synchronously and returns one large,
nested JSON value.

The recorded exchange shows nested objects, arrays, empty
objects, dates, URLs, booleans, and numbers unchanged. A field such as
`is_partial` belongs to the process result and must not be read as an OGC job
status.

See
[`../recorded-exchanges/execution-sync/deeply-nested-json-output/`](../recorded-exchanges/execution-sync/deeply-nested-json-output/).
The recorded response avoids calling PDOK during normal tests.
