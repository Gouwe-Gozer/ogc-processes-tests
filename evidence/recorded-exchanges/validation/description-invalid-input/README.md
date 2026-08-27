# Wrong primitive input type is accepted by the server but should fail client preflight

Process: `longProcess`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative scenario set.

## Validation observation

Expected: `invalid`
- `inputs.sid`: integer or null; received: string

## submit-invalid-body

Handling: `description-validation-error`

Expected client handling

- Identify inputs.sid and report that the description requires an integer or null, not a string.
- Preserve the user's original value; do not silently coerce it.
- If an explicit raw submission bypasses generated-form validation, still interpret HTTP 201 as job accepted and make the job dismissible.

Avoid

- Send this body from the ordinary description-driven form flow.
- Conclude that the process description permits strings because this server accepted one.
- Report process success from the observed HTTP 201.

## cleanup-if-sent

Handling: `job-dismissed`

Expected client handling

- Use explicit DELETE to clean up the server job if the manual submission step was executed.

Avoid

- Assume cancelling the local POST removed the accepted job.
