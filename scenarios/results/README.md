# Result scenarios

This section contains output descriptions and recorded results for testing how
the client finds a semantic payload and chooses a useful presentation.

```text
results/
├── maps/<provider>/<scenario>/
├── tables/<provider>/<scenario>/
├── values/<provider>/<scenario>/
└── downloads/<provider>/<scenario>/
```

- `maps/` contains spatial values that can be presented with MapLibre.
- `tables/` contains row-and-column data such as CSV.
- `values/` contains scalars, bounding boxes and ordinary JSON.
- `downloads/` contains references, large bodies and formats without a
  built-in renderer.

A scenario normally contains the output description and the execution that
returned the value:

```text
01-get-description.request.json
01-get-description.response.json
02-execute.request.json
02-execute.response.json
README.md
```

Each README links to the original evidence. A scenario has one main category,
but the UI may offer more than one presentation. For example, CSV can have a
table preview and a download.

## Stored response versus API response

A response file in this repository has capture metadata around the real HTTP
body:

```json
{
  "status": 200,
  "headers": {
    "Content-Type": "application/json"
  },
  "final_url": "https://example.com/processes/example/execution",
  "body": {
    "Result": {
      "value": "the semantic payload"
    }
  }
}
```

The outer `status`, `headers`, `final_url` and `body` fields belong to the
evidence format. A live API response contains the value stored in `body`, not
that outer capture object.

## From response body to semantic payload

There are three separate layers:

```text
HTTP response → result document → output value
```

The client already knows whether it requested a raw or document response. It
should use that request context, the output description, the returned media
type and the actual result wrapper together. It should not search arbitrary
JSON recursively for properties called `value`, `href` or `outputs`.

### Document response

The standard document form is an object keyed by output ID. An output can be a
direct value, a qualified inline value, a link, a bounding box, or an array of
these values.

Direct scalar:

```json
{
  "Distance": 12.5
}
```

Qualified inline value:

```json
{
  "Result": {
    "value": {
      "type": "FeatureCollection",
      "features": []
    }
  }
}
```

The semantic payload is `Result.value`, while `Result` remains the output ID.

Referenced value captured from ZOO:

```json
{
  "OUTPUT": {
    "href": "https://example.com/result.tif",
    "format": {
      "mediaType": "image/tiff"
    }
  }
}
```

Weaver instead records the media type beside `href`:

```json
{
  "featureCollectionOutput": {
    "href": "https://example.com/result.geojson",
    "type": "application/geo+json"
  }
}
```

The successful Weaver job under
[`../protocol/jobs/weaver-local/successful-job`](../protocol/jobs/weaver-local/successful-job/)
contains direct scalars, an array, a bounding box, several links and repeated
linked geometry outputs in one document.

### Raw response

A raw response has no result document. The HTTP body itself is the semantic
payload and the HTTP `Content-Type` identifies its representation. The
[`downloads/directed-local/large-raw-csv`](downloads/directed-local/large-raw-csv/)
scenario therefore treats the complete response body as CSV rather than
looking for an output ID or `value` property.

### Provider variations

The captured pygeoapi hello-world document uses an array:

```json
{
  "outputs": [
    {
      "id": "echo",
      "value": "Hello"
    }
  ]
}
```

Its raw JSON response is another object containing `id` and `value`. Both are
kept in
[`../protocol/execution/pygeoapi-demo/raw-versus-document-response`](../protocol/execution/pygeoapi-demo/raw-versus-document-response/).
They are recorded provider behaviour, not a reason to unwrap every object with
a `value` property.

The standard distinction between document and raw results is described in the
[OGC API Processes Core response requirements](https://docs.ogc.org/is/18-062r2/18-062r2.html#toc61).

## Choosing a presentation

Use the output description as the starting point. Confirm it with the selected
output format, the returned media type and the actual payload. An output ID or
title is only a label and must not decide the renderer by itself.

| Semantic payload | Default presentation | Important checks |
|---|---|---|
| String, number or Boolean | Text or a simple value field | Preserve the original type |
| Ordinary JSON object | Structured JSON view and download | Do not treat all JSON as GeoJSON or flatten nested objects |
| Array of primitives | List or small table, plus JSON download | Preserve order and item types |
| Array of similarly shaped objects | Table and JSON download | Fall back to JSON when columns are irregular or deeply nested |
| CSV | Table preview and download | Respect encoding; avoid eagerly rendering very large bodies |
| GeoJSON Geometry, Feature or FeatureCollection | MapLibre map and GeoJSON download | Preserve properties, geometry type, CRS information and extra coordinates |
| Bounding box | Rectangle on a map and numeric values | Check coordinate count, axis order and CRS |
| GeoJSON link | Fetch and map when browser access and parsing succeed; otherwise download/open | Respect CORS and the returned media type |
| TIFF, GML, KML, LAS or another unsupported file | Download/open action | Only promise a map when a suitable parser or source implementation exists |
| Unknown media type or unsupported schema | Raw body or JSON view and download | Preserve the original value and metadata |

The tender promises a raw JSON fallback for unsupported schemas. A richer
domain-specific renderer can be added later without changing how the original
payload is preserved.

## MapLibre output diversity

MapLibre can receive a GeoJSON object or a URL that resolves to GeoJSON through
a GeoJSON source. Geometry type still matters because points, lines and areas
need different style layers.

| GeoJSON case | Scenario | UI concern |
|---|---|---|
| Polygon FeatureCollection | [`maps/zoo-local/geojson-value`](maps/zoo-local/geojson-value/) | Fill, outline and feature properties |
| Bare LineString Geometry | [`maps/zoo-local/geojson-geometry-value`](maps/zoo-local/geojson-geometry-value/) | Geometry without Feature or FeatureCollection wrapper; third coordinate |
| Several named Point, LineString and Polygon collections | [`maps/zoo-local/multiple-featurecollections`](maps/zoo-local/multiple-featurecollections/) | Separate output labels and layers |
| LineString and MultiLineString in one collection | [`maps/zoo-local/line-and-multiline`](maps/zoo-local/line-and-multiline/) | Same line style family, different coordinate nesting |
| MultiPolygon | [`maps/zoo-local/multipolygon`](maps/zoo-local/multipolygon/) | Preserve multiple polygon parts and rings |
| GeometryCollection | [`maps/zoo-local/geometry-collection`](maps/zoo-local/geometry-collection/) | Several geometry members may require several style layers |
| Linked GeoJSON | [`../protocol/jobs/weaver-local/successful-job`](../protocol/jobs/weaver-local/successful-job/) | Fetch subject to CORS; keep download fallback |
| Bounding box | [`values/zoo-local/scalar-object-and-bbox`](values/zoo-local/scalar-object-and-bbox/) | Convert to a rectangle only after checking CRS and axis order |

Feature properties can also support a popup or attribute table. That is an
additional view of the same feature data, not a reason to remove properties
before giving the GeoJSON to MapLibre.

The MapLibre GeoJSON source API is documented in
[MapLibre GL JS: GeoJSONSource](https://maplibre.org/maplibre-gl-js/docs/API/classes/GeoJSONSource/).

## Non-map result diversity

| Result | Scenario | Expected presentation |
|---|---|---|
| Inline CSV in `RESULT.value` | [`tables/zoo-local/inline-csv`](tables/zoo-local/inline-csv/) | Table and CSV download |
| Large raw CSV body | [`downloads/directed-local/large-raw-csv`](downloads/directed-local/large-raw-csv/) | Download and limited or paginated preview |
| Deeply nested ordinary JSON | [`values/bgt-prototype/deeply-nested-json`](values/bgt-prototype/deeply-nested-json/) | Structured JSON view and download |
| Direct string, qualified object and bbox in one document | [`values/zoo-local/scalar-object-and-bbox`](values/zoo-local/scalar-object-and-bbox/) | Text, JSON and optional map rectangle |
| TIFF returned by reference | [`downloads/zoo-local/result-by-reference`](downloads/zoo-local/result-by-reference/) | Download/open action |
| Direct and linked Weaver outputs | [`../protocol/jobs/weaver-local/successful-job`](../protocol/jobs/weaver-local/successful-job/) | Select a presentation separately for every output ID |

## Important findings

- The output ID identifies the result but does not identify its semantic type.
- `application/json` can describe ordinary JSON or GeoJSON. Use schema hints,
  returned format information and the payload structure together.
- A document can contain several outputs that need different presentations.
- An `href` is a usable reference. A server filesystem path returned as a
  string is not a browser download URL.
- A successful execution does not guarantee that a referenced result is
  reachable from the browser. Keep the link and media type and report fetch or
  CORS failures clearly.
- Preserve the complete original payload even when the UI also derives map
  layers, table rows or a preview from it.

## Coverage still missing

The repository does not yet contain:

- a MultiPoint result;
- a successful browser-accessible linked GeoJSON result;
- an inline base64-encoded result;
- a raw binary response body;
- a `multipart/related` raw response containing several outputs;
- a successful result that can be rendered as a raster map without adding a
  separate GeoTIFF or COG reader.

These are evidence gaps, not reasons to invent provider responses. Until a
real example is captured, the client should use its generic JSON or download
fallback.
