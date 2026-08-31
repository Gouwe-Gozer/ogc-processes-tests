# Local BGT prototype

This deployment points to the unfinished local `bgt-land-cover-summary`
process. Its discovery resources and process description were captured on 31
August 2026. It runs synchronously and returns one large, nested JSON value.

The recorded exchange shows nested objects, arrays, empty
objects, dates, URLs, booleans, and numbers unchanged. A field such as
`is_partial` belongs to the process result and must not be read as an OGC job
status.

The evidence contains:

- [`captures/discovery/core-discovery/`](captures/discovery/core-discovery/);
- [`captures/descriptions/bgt-land-cover-summary/`](captures/descriptions/bgt-land-cover-summary/);
- [`captures/executions/deeply-nested-json-output/`](captures/executions/deeply-nested-json-output/).

The recorded execution response avoids calling PDOK during normal tests.
