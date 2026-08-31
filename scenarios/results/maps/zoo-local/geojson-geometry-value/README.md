# Inline GeoJSON Geometry

Process: `GdalExtractProfile`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/GdalExtractProfile/)
- [successful execution](../../../../../evidence/zoo-local/captures/executions/gdal_extract_profile_line/)

The result is a bare GeoJSON LineString rather than a Feature or
FeatureCollection. Its semantic payload and media type are:

```text
body.Profile.value
body.Profile.format.mediaType
```

The LineString can be passed to a MapLibre GeoJSON source and displayed with a
line layer. Its coordinates contain elevation as a third value. The map may
display only two dimensions, but the client must preserve the third value.

This is result-only material. The recorded execution uses filenames inside
the ZOO container and is not an example for browser file input.
