# HTTP success omits the requested repeated output

Process: `SAGA.grid_tools.27`
Source server: `zoo-local`
Selected as [`errors/zoo-local/missing-requested-output`](../../../../../scenarios/errors/zoo-local/missing-requested-output/).

## Why it may be useful

- Repeated complex output requested by exact ID.
- Empty HTTP-200 document demonstrates result completeness is separate from status.

## execute

Handling: `synchronous-result-incomplete`

Expected client handling

- Retain the empty raw response and report that requested output TILES is missing.
- Expose HTTP execution success separately from result completeness.

Avoid

- Return an empty successful TILES array that the server did not send.
- Treat the missing output as a no-response network error.
- Guess that no tiles is a valid algorithm result.
