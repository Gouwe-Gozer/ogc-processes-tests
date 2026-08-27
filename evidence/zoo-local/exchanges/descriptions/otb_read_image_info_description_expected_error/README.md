# One advertised process description returns non-JSON HTTP 500

Process: `OTB.ReadImageInfo`
Source server: `zoo-local`
Selected as [`errors/zoo-local/process-description-html-error`](../../../../../scenarios/errors/zoo-local/process-description-html-error/).

## Why it may be useful

- Collection discovery can succeed while one individual description fails.
- The endpoint returns HTML despite an application/json request.

## get-description

Handling: `process-description-unavailable`

Expected client handling

- Keep the rest of the process collection usable and mark only OTB.ReadImageInfo as unavailable.
- Return status, headers, final URL, and raw HTML with a safe generic message.

Avoid

- Attempt to construct an execution form from a missing description.
- Render the returned HTML as trusted application markup.
- Fail or discard all previously discovered processes.
