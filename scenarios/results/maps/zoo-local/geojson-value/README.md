# Synchronous GeoJSON value

This scenario was captured from the ZOO `Buffer` process on 25 August 2026.

Original evidence:

- [successful execution](../../../../../evidence/zoo-local/captures/executions/buffer_polygon/)

It combines a GeoJSON input supplied by URL with a numeric literal. The server
returns HTTP 200 and a document response containing `Result.value`, whose value
is a GeoJSON FeatureCollection.

This scenario is useful for checking that a client keeps the output ID, the
`value` wrapper, the requested media type, and the complete GeoJSON value.
Geometry validation belongs outside the protocol core.
