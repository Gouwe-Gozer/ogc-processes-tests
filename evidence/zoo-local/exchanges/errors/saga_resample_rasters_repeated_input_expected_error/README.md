# Advertised repeated raster input causes a provider crash

Process: `SAGA.grid_tools.0`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative scenario set.

## Why it may be useful

- Array cardinality permitted by maxOccurs.
- One href item and one inline base64 item in the same complex array.

## execute

Handling: `synchronous-http-problem`

Expected client handling

- Allow this request through description-based validation.
- Display the server crash detail safely and retain the exact array order and raw problem.

Avoid

- Claim that repeated INPUT is schema-invalid.
- Identify either raster as the cause from SIGSEGV alone.
- Automatically retry with one input or silently discard the second value.
