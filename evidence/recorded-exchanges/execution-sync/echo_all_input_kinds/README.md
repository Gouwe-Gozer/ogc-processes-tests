# Mixed optional literal, complex, and bounding-box values

Process: `EchoProcess`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative example set.

## Why it may be useful

- Optional inputs must remain omitted rather than becoming null.
- Wrapped JSON, bounding box, and multiple heterogeneous result IDs.

## execute

Handling: `synchronous-results-available`

Expected client handling

- Preserve each named output independently, including the complex value wrapper and bounding-box CRS.
- Retain the order and numeric zero-capability of bounding-box coordinates.

Avoid

- Flatten complexOutput.value into an unrelated literal shape.
- Assume all outputs from one execution share a value type.
