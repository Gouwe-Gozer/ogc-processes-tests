# Referenced raster produces a TIFF result by reference

Process: `SAGA.grid_tools.0`
Source server: `zoo-local`
Selected as [`sync/zoo-local/result-by-reference`](../../../../../scenarios/sync/zoo-local/result-by-reference/).

## Why it may be useful

- Referenced AAIGrid plus Boolean, enum, and numeric controls.
- A repeatable input represented as a singleton object when only one value is supplied.
- Complex raster output transmitted by reference.

## execute

Handling: `synchronous-results-available`

Expected client handling

- Expose the output href and declared image/tiff media type as a reference.
- Keep reference retrieval failure separate from execution status if a later fetch fails.

Avoid

- Treat the href string as inline TIFF data.
- Persist or download the raster inside the protocol core without a consumer request.
