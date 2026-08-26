# Description-conformant GDAL request fails without actionable detail

Process: `Gdal_Grid`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative example set.

## Why it may be useful

- Advertised server-side filename inputs reach the provider.
- Problem response contains a generic fallback instead of an input-specific cause.

## execute

Handling: `synchronous-http-problem`

Expected client handling

- Expose a generic request-failed summary with the server detail and raw problem.
- Retain that the submitted body conforms to the captured description.

Avoid

- Invent unadvertised layer or band parameters.
- Blame the fixture or a specific input without response evidence.
- Automatically retry the POST.
