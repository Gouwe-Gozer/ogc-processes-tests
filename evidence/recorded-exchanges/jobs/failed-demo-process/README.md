# Accepted asynchronous submission reaches a failed terminal state

Process: `demo`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative scenario set.

## submit

Handling: `job-accepted`

Expected client handling

- Expose an accepted job and keep submission evidence separate from later status responses.

Avoid

- Report process success from HTTP 201.
- Predict failure merely because this test process is known to fail.

## poll-failed

Handling: `job-failed`

Expected client handling

- Stop polling at the failed terminal state.
- Expose the exact server message and retain the complete raw status document.
- Keep HTTP retrieval success separate from process-job failure.

Avoid

- Fetch a successful results document when no results relation is advertised.
- Replace the server message with a guessed input error.
- Automatically re-submit the non-idempotent execution request.
