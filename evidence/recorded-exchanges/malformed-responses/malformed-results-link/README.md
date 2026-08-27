# Successful job advertises an OGC results relation with an invalid URL

Stored as supporting evidence; it is not part of the small representative scenario set.

## poll-successful

Handling: `job-successful-results-link-invalid`

Expected client handling

- Expose the job itself as successfully completed.
- Report link-resolution failure separately and retain the original href and raw job document.

Avoid

- Attempt a fetch using the malformed URL.
- Fall back to a link chosen by title or position.
- Turn the terminal job status into provider failure.
