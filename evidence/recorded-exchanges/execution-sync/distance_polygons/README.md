# Two referenced geometries produce a numeric result

Process: `Distance`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative scenario set.

## Why it may be useful

- Multiple complex references with explicit media types.
- A valid numeric result whose value is zero.

## execute

Handling: `synchronous-results-available`

Expected client handling

- Preserve reference order and media type in the execution body.
- Expose numeric zero as a valid present result.

Avoid

- Treat zero as missing or false because of a truthiness check.
- Assume that advertised generic geometry wording guarantees every geometry subtype works.
