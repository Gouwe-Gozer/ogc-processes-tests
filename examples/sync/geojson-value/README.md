# Synchronous GeoJSON value

This example was captured from the ZOO `Buffer` process on 25 August 2026.

It combines a GeoJSON input supplied by URL with a numeric literal. The server
returns HTTP 200 and a document response containing `Result.value`, whose value
is a GeoJSON FeatureCollection.

This example is useful for checking that a client keeps the output ID, the
`value` wrapper, the requested media type, and the complete GeoJSON value.
Geometry validation belongs outside the protocol core.
