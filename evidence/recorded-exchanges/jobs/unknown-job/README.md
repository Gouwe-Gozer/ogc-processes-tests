# Retrieve a syntactically valid but unknown job identifier

Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative example set.

## get-unknown-job

Handling: `job-resource-missing`

Expected client handling

- Expose the parsed NoSuchJob problem together with status, headers, final URL, and raw body.
- Keep an existing caller-side job record available for diagnostics.

Avoid

- Automatically re-submit the process.
- Treat an HTTP 404 response as a transport failure with no response.
- Guess whether the job expired, was dismissed, belonged to another user, or never existed.
