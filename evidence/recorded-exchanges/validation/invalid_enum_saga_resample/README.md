# Unadvertised SAGA enum value is accepted by the provider

Process: `SAGA.grid_tools.0`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative example set.

## Why it may be useful

- Description-driven enum validation and exact value preservation.
- Server HTTP success does not expand the enum advertised to a generic client.

## Validation observation

Expected: `invalid`
- `inputs.TARGET_DEFINITION`: enum: user defined or grid or grid system; received: not advertised

## execute-invalid-body

Handling: `description-validation-error`

Expected client handling

- List the two advertised TARGET_DEFINITION values and normally block submission.
- If explicitly sent as raw JSON, preserve the original value and parse the returned reference without changing the captured contract.

Avoid

- Silently replace the unknown value with the default.
- Conclude that not advertised became a supported enum member because this provider returned HTTP 200.
- Send this request from the ordinary description-driven form flow.
