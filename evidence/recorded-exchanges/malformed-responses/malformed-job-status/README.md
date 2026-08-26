# Job polling returns HTTP 200 with malformed JSON

Stored as supporting evidence; it is not part of the small representative example set.

## poll

Handling: `invalid-job-document`

Expected client handling

- Return a protocol parsing error containing status, headers, final URL, and raw body.
- Stop a poll-until-terminal helper and let the caller decide whether a later GET is appropriate.

Avoid

- Mark the job successful or failed.
- Turn the HTTP response into a no-response network error.
- Re-submit the process execution.
