# Linked GeoJSON line and polygon

Process: `SAGA.shapes_lines.3`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/SAGA.shapes_lines.3/)
- [successful execution](../../../../../evidence/zoo-local/captures/executions/saga_line_polygon_intersection/)

The request supplies one GeoJSON FeatureCollection containing a LineString and
one containing a Polygon. Both are links with `type: application/json`. A third
enum input controls which properties are retained. The recorded execution
succeeded with these inputs.

After loading the links, MapLibre can display both FeatureCollections, but the
line and polygon need different drawing styles and editing tools. The process
description identifies them through titles, not a reliable GeoJSON subtype
schema, so subtype validation should be based on the loaded value rather than
the input ID.
