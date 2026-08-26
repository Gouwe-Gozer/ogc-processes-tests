# Successful job status omits the results relation

Stored as supporting evidence; it is not part of the small representative example set.

## poll-successful

Handling: `job-successful-results-location-missing`

Expected client handling

- Expose the job itself as successfully completed.
- Report separately that the response has no advertised OGC results resource.
- Preserve all links and the raw job document for diagnostics.

Avoid

- Change the terminal job status to failed.
- Invent a results URL or return an empty successful result.
- Keep polling a terminal job in the hope that a link appears.
