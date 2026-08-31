# MultiPolygon result

Process: `SymDifference`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/SymDifference/)
- [successful execution](../../../../../evidence/zoo-local/captures/executions/symmetric_difference_polygons/)

The semantic payload at `body.Result.value` is a FeatureCollection containing
a MultiPolygon. It uses the same MapLibre fill and outline presentation family
as Polygon, but the nested coordinate structure must be preserved.
