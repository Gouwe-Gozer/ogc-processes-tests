# Five-number bounding box violates the advertised four-or-six constraint

Process: `EchoProcess`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative scenario set.

## Why it may be useful

- Nested oneOf array cardinality in a bounding-box object.
- Server HTTP success does not override description-driven client validation.

## Validation observation

Expected: `invalid`
- `inputs.c.bbox`: oneOf: exactly 4 or exactly 6 items; received: 5 items

## execute-invalid-body

Handling: `description-validation-error`

Expected client handling

- Report that inputs.c.bbox requires four or six numbers and normally block submission.
- If explicitly sent as raw JSON, parse and preserve the HTTP-200 response without changing the advertised constraint.

Avoid

- Silently remove, duplicate, or reorder a coordinate.
- Conclude that five-number boxes are valid because this server echoed one.
- Send this request from the ordinary description-driven form flow.
