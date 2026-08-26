# One raster produces two named inline vector outputs

Process: `SAGA.shapes_grid.5`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative example set.

## Why it may be useful

- Raster reference with numeric and Boolean controls.
- Multiple named complex outputs in one document.

## execute

Handling: `synchronous-results-available`

Expected client handling

- Expose both requested output IDs independently of their order in the JSON object.
- Preserve each qualified GeoJSON value and retain the requested media type as request context.

Avoid

- Return only the first complex output.
- Build a fixed two-output limit into the result model.
- Invent response format fields that the server omitted.
