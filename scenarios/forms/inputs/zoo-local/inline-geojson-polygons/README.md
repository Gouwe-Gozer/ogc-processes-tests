# Inline GeoJSON polygon features

Process: `SAGA.shapes_polygons.5`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/SAGA.shapes_polygons.5/)
- [successful execution](../../../../../evidence/zoo-local/captures/executions/saga_dissolve_polygons/)

The request contains an inline GeoJSON FeatureCollection with two Polygon
features and their properties. ZOO wraps the object in `value` and adds a
nested `format` with `mediaType: application/json`. It also includes Boolean
and numeric controls. The recorded execution succeeded with these inputs.

MapLibre can display the FeatureCollection immediately because no additional
file fetch is required. The form must retain feature properties and the full
FeatureCollection wrapper instead of extracting only the coordinates.
