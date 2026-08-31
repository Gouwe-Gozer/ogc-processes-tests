# Inline Polygon FeatureCollection

This scenario was captured from the ZOO `Buffer` process on 25 August 2026.

Original evidence:

- [successful execution](../../../../../evidence/zoo-local/captures/executions/buffer_polygon/)

The result document contains one output called `Result`. Its semantic payload
is the GeoJSON FeatureCollection at:

```text
body.Result.value
```

The collection contains a Polygon feature and ordinary feature properties.
The UI can show the geometry with a MapLibre fill and outline layer and expose
the properties in a popup or table. The `Result` output ID and the `value`
wrapper are not part of the GeoJSON payload passed to MapLibre.
