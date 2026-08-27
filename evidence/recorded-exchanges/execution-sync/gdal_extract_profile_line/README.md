# Server filename and remote line produce structured profile coordinates

Process: `GdalExtractProfile`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative scenario set.

## Why it may be useful

- Mixed server-side filename literal and complex reference.
- Qualified JSON LineString with three-dimensional coordinates.

## execute

Handling: `synchronous-results-available`

Expected client handling

- Preserve the Profile.value and Profile.format wrapper.
- Retain coordinate tuples of arbitrary supported length, including the elevation ordinate.

Avoid

- Rewrite RasterFile into a browser file URL.
- Discard the third coordinate because a map renderer may only use two dimensions.
