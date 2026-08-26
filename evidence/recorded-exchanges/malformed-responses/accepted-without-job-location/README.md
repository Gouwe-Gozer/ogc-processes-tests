# Accepted submission has neither a Location header nor a usable monitor link

Stored as supporting evidence; it is not part of the small representative example set.

## submit

Handling: `accepted-job-location-missing`

Expected client handling

- Report that the server accepted a job but did not provide a usable monitor URL.
- Preserve the jobID, response status, headers, final URL, parsed body, and raw body for diagnostics.

Avoid

- Report process success.
- Invent a monitor URL from the job ID alone.
- Repeat the POST in an attempt to obtain a better response.
