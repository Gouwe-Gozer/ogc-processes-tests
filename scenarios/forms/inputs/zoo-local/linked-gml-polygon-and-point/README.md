# Linked GML geometry inputs

Process: `Contains`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/Contains/)
- [successful execution](../../../../../evidence/zoo-local/captures/executions/contains_polygon_point/)

The request contains two required complex inputs. One link refers to a GML
FeatureCollection containing a Polygon and the other to a GML FeatureCollection
containing a Point. Both are represented by an `href` and `type` object.

A generated form should allow a URL to be supplied for each input, retain the
selected `text/xml` media type, and keep the Polygon under `InputEntity1` and
the Point under `InputEntity2`. The client should not download and rewrite the
referenced files while building the execution request.

The successful Boolean response proves that ZOO accepted this request shape.

GML is not a direct MapLibre GeoJSON source. Without a GML parser, these inputs
should use URL/file controls and should not promise a map preview.
