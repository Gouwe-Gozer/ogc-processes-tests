# Several named GeoJSON outputs

Process: `SAGA.tin_tools.2`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/SAGA.tin_tools.2/)
- [successful execution](../../../../../evidence/zoo-local/captures/executions/saga_shapes_to_tin/)

One result document contains five output IDs. Each output has its own
FeatureCollection under `value`:

```text
body.TIN_POINTS.value
body.TIN_CENTER.value
body.TIN_EDGES.value
body.TIN_TRIANGLES.value
body.TIN_POLYGONS.value
```

Together they contain Point, LineString and Polygon features. The UI should
keep the output IDs visible and create suitable MapLibre layers for each
collection. It must not merge the five outputs into one anonymous payload.

Several coordinates contain a third value. Preserve it even when the map view
is two-dimensional.
