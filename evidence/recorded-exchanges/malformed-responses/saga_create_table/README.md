# Advertised table result is an unavailable TIFF reference

Process: `SAGA.table_tools.0`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative example set.

## Why it may be useful

- Description metadata advertises raster media types for a logical table output.
- A syntactically valid reference wrapper can point to a missing resource.

## execute

Handling: `synchronous-reference-advertised`

Expected client handling

- Expose the reference and its declared media type without silently correcting the process description.
- Keep execution status separate from a later retrieval attempt.

Avoid

- Invent a CSV/table format that was not advertised or returned.
- Claim that the referenced content exists from HTTP 200 alone.

## fetch-reference

Handling: `result-reference-unavailable`

Expected client handling

- Report reference retrieval failure separately from the successful execution.
- Retain the result href, retrieval status, headers, final URL, and raw HTML.

Avoid

- Render returned HTML as trusted markup.
- Rewrite the execution itself as an HTTP failure.
- Return an empty table as if retrieval succeeded.
