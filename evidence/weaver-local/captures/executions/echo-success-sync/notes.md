# Successful synchronous execution with varied input and output types

`EchoProcess` accepts ten required inputs and returns HTTP 200 within the
requested wait period. The result document combines inline primitive values,
an array, a bounding box, and links to JSON, GeoJSON, and TIFF outputs.

Although the caller requested synchronous execution, Weaver also records the
execution as a job and advertises job, result, output, log, and provenance links
in the response headers.
