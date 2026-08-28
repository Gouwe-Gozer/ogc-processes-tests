# Required hellojs input is omitted

Process: `hellojs`
Source server: `zoo-local`
Selected as [`protocol/errors/zoo-local/missing-required-input`](../../../../../scenarios/protocol/errors/zoo-local/missing-required-input/).

## Why it may be useful

- Requiredness must use the exact opaque input ID.
- A server can return a useful structured problem if raw invalid input is sent.

## Validation observation

Expected: `invalid`
- `inputs.S`: required; received: absent

## execute-invalid-body

Handling: `description-validation-error`

Expected client handling

- Identify inputs.S as required and normally block submission.
- If explicitly sent as raw JSON, safely display the server problem and retain its raw body.

Avoid

- Invent an empty string or null default.
- Derive the required key from the title Name.
- Send this request from the ordinary description-driven form flow.
