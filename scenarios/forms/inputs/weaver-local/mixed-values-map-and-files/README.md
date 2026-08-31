# Mixed values, map inputs, and files

Process: `EchoProcess`
Source server: `weaver-local`

Original evidence:

- [process description](../../../../../evidence/weaver-local/captures/descriptions/EchoProcess/)
- [successful synchronous execution](../../../../../evidence/weaver-local/captures/executions/echo-success-sync/)

This is the broadest successful form example in the repository. Its request
contains:

- an enum string;
- a measurement and unit object;
- a date-time string and a number;
- an integer array;
- an ordinary JSON object;
- a GeoJSON Point and Polygon;
- a bounding box with a CRS;
- an inline base64 TIFF; and
- a GeoJSON FeatureCollection containing a Point feature.

The description distinguishes ordinary JSON, GeoJSON Geometry, and GeoJSON
FeatureCollection values through formats and content schemas. A form can use
normal controls for primitive fields, a JSON editor for the object, a bbox
control, a map input for GeoJSON, and a file input for the image.

MapLibre can display the Point, Polygon, and FeatureCollection values. It does
not make the TIFF a direct map source. The third coordinate in the point
feature must remain in the submitted value even if the map view ignores it.

The successful recorded execution confirms that Weaver accepted these input
encodings.
