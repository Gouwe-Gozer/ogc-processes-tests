# Server-side raster filenames return a server-local path

Process: `Gdal_Translate`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative scenario set.

## Why it may be useful

- Literal filename inputs whose meaning is defined by the server environment.
- Successful result is a server-local path rather than a retrievable API reference.

## execute

Handling: `synchronous-server-path-result`

Expected client handling

- Expose the returned path as a literal server result with a clear server-local warning.
- Retain the exact request and response for profile diagnostics.

Avoid

- Prefix the path with baseUrl or attempt to fetch it from the browser.
- Suggest that local fixture staging is intended final-client behaviour.
- Claim the path is downloadable merely because execution returned HTTP 200.
