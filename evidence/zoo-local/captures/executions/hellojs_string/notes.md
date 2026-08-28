# Minimal synchronous literal execution

Process: `hellojs`
Source server: `zoo-local`
Selected as
[`protocol/execution/zoo-local/simple-sync`](../../../../../scenarios/protocol/execution/zoo-local/simple-sync/).

## Why it may be useful

- Required primitive input keyed by opaque ID.
- Inline string output in a document response.

## execute

Handling: `synchronous-results-available`

Expected client handling

- Expose the returned result string and retain the raw document.
- Treat the literal value as present even when it is an empty string in another response.

Avoid

- Derive the input or output ID from its human-readable title.
- Require an outputs object when the process accepts the shorter request.
