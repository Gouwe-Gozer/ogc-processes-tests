# Linked raster with contour controls

Process: `SAGA.shapes_grid.5`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/SAGA.shapes_grid.5/)
- [successful execution](../../../../../evidence/zoo-local/captures/executions/saga_contours_raster/)

The request supplies an AAIGrid raster through `href` and `type`, followed by
numeric interval values and Boolean choices. The recorded execution succeeded
with these inputs.

The generated UI needs a file-or-URL control for the raster and ordinary
number and checkbox controls for the options. AAIGrid is not a direct MapLibre
source. A map preview would require a raster reader or conversion step that is
outside the request serializer.
