# Two referenced vectors produce one wrapped vector result

Process: `Intersection`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative scenario set.

## Why it may be useful

- Reusable two-reference execution envelope.
- Inline vector result wrapper shared by several GEOS operations.

## execute

Handling: `synchronous-results-available`

Expected client handling

- Expose the wrapped FeatureCollection under the requested Result ID.
- Retain unknown feature properties without schema-specific filtering.

Avoid

- Add operation-specific intersection logic to the generic protocol core.
- Require the output geometry to equal a hard-coded coordinate sequence.
