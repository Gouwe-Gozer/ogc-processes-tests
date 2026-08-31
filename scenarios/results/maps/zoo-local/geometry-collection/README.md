# GeometryCollection result

Process: `Delaunay`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/Delaunay/)
- [successful execution](../../../../../evidence/zoo-local/captures/executions/delaunay_five_points/)

The semantic payload at `body.Result.value` is a FeatureCollection whose
features contain GeometryCollection values. Each collection contains several
geometry members.

The UI must preserve the GeometryCollection. A map presentation may need more
than one MapLibre style layer when its members include different geometry
families. A raw GeoJSON view or download remains available if the application
cannot provide a useful combined style.
