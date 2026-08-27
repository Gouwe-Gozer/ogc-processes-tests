# Inline base64 LAS request terminates with SIGSEGV

Process: `SAGA.pointcloud_tools.4`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative scenario set.

## Why it may be useful

- Binary complex input represented as base64 with explicit media type and encoding.
- Multiple requested raster outputs combined with a provider crash.

## execute

Handling: `synchronous-http-problem`

Expected client handling

- Validate the wrapper and base64 syntax without promising semantic LAS validity.
- Preserve both requested output IDs and show the provider detail safely.

Avoid

- Treat successful base64 decoding as proof that the provider can import the point cloud.
- Blame GRID or COUNT output selection from the generic crash message.
- Retry or rewrite the request automatically.
