# Linked GeoJSON points and raster

Process: `SAGA.shapes_grid.0`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/SAGA.shapes_grid.0/)
- [successful execution](../../../../../evidence/zoo-local/captures/executions/saga_add_grid_values_points/)

The request combines a linked GeoJSON FeatureCollection of Point features with
a linked AAIGrid raster. Both use `href` and `type`, followed by an ordinary
enum string. The recorded execution succeeded with these inputs.

The GeoJSON point data can be shown in MapLibre after the browser successfully
fetches the URL. The AAIGrid file is not a direct MapLibre source and should use
a generic file or URL control unless raster conversion is added separately.

The description calls the first input `Points`, but it does not provide a
machine-readable GeoJSON Point constraint. The title can be shown to the user;
it should not be used as schema validation.
