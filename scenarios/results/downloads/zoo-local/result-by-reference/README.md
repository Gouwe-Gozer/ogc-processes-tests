# Result returned by reference

Process: `SAGA.grid_tools.0`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/SAGA.grid_tools.0/)
- [successful execution](../../../../../evidence/zoo-local/captures/executions/saga_resample_rasters/)

The request supplies a referenced raster and asks for the output with
`transmissionMode: reference`. The response returns an `href` and the declared
`image/tiff` media type.

The result location and media type are:

```text
body.OUTPUT.href
body.OUTPUT.format.mediaType
```

The UI should present the URL as a download or open action. A GeoTIFF is not a
GeoJSON value that can be passed directly to a MapLibre GeoJSON source. A map
preview would require separate GeoTIFF or COG support.
