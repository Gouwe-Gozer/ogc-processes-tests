# LineString and MultiLineString results

Process: `SAGA.shapes_grid.5`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/SAGA.shapes_grid.5/)
- [successful execution](../../../../../evidence/zoo-local/captures/executions/saga_contours_raster/)

The result document contains two named FeatureCollections:

```text
body.CONTOUR.value
body.POLYGONS.value
```

`CONTOUR` contains both LineString and MultiLineString features. `POLYGONS`
contains Polygon features. MultiLineString belongs to the same MapLibre line
presentation family as LineString, but it must remain a distinct GeoJSON
geometry type in the payload.
