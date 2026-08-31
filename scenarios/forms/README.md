# Form scenarios

This section contains process descriptions and execution requests for testing
generated forms and the values those forms place in an execution request.

The examples are also reference material for the front-end developer. They
show which controls are justified by the process description, which values can
be previewed with MapLibre, and when the UI needs a generic file, URL, or raw
JSON control instead.

## Folder structure

```text
forms/
├── inputs/<provider>/<scenario>/
└── validation/<provider>/<scenario>/
```

- `inputs/` contains accepted requests with representative input data.
- `validation/` contains incomplete descriptions, unusual serialization, or
  inputs allowed by the description that still fail at the provider.
- `<provider>` matches a directory under [`../../evidence/`](../../evidence/)
  and supplies the base URL used by the Postman generator.

A normal scenario contains:

```text
01-get-description.request.json
01-get-description.response.json
02-execute.request.json
02-execute.response.json
README.md
```

Each scenario README links to the original evidence and explains the expected
form control, request encoding, and any MapLibre limitation.

## Successful input examples

| Process and scenario | Data represented | Main UI concern |
|---|---|---|
| pygeoapi `hello-world` in [`../protocol/execution/pygeoapi-demo/raw-versus-document-response`](../protocol/execution/pygeoapi-demo/raw-versus-document-response/) | Required and optional strings, Boolean and defaults | Basic generated controls |
| BGT `bgt-land-cover-summary` in [`inputs/bgt-prototype/numeric-ranges`](inputs/bgt-prototype/numeric-ranges/) | Numbers and integers with ranges and defaults | Numeric constraints |
| Weaver `EchoProcess` in [`inputs/weaver-local/mixed-values-map-and-files`](inputs/weaver-local/mixed-values-map-and-files/) | Enum, date-time, units, array, JSON object, bbox, Point, Polygon, FeatureCollection and TIFF | Mixed controls and qualified values |
| ZOO `Contains` in [`inputs/zoo-local/linked-gml-polygon-and-point`](inputs/zoo-local/linked-gml-polygon-and-point/) | GML Polygon and Point supplied by URL | Linked non-GeoJSON geometry |
| ZOO `SAGA.shapes_grid.0` in [`inputs/zoo-local/linked-geojson-points-and-raster`](inputs/zoo-local/linked-geojson-points-and-raster/) | GeoJSON point features and an AAIGrid raster supplied by URL | Map data and non-map file in one form |
| ZOO `SAGA.shapes_lines.3` in [`inputs/zoo-local/linked-geojson-line-and-polygon`](inputs/zoo-local/linked-geojson-line-and-polygon/) | Linked GeoJSON LineString and Polygon FeatureCollections | Different map geometry shapes |
| ZOO `SAGA.shapes_polygons.5` in [`inputs/zoo-local/inline-geojson-polygons`](inputs/zoo-local/inline-geojson-polygons/) | Inline GeoJSON FeatureCollection with several Polygon features | Inline map data and feature properties |
| ZOO `SAGA.shapes_grid.5` in [`inputs/zoo-local/linked-raster`](inputs/zoo-local/linked-raster/) | Linked AAIGrid raster with numeric and Boolean controls | Generic raster input |
| ZOO `SAGA.table_tools.3` in [`inputs/zoo-local/inline-csv`](inputs/zoo-local/inline-csv/) | Two inline UTF-8 CSV tables | Multiline/file input and encoding |

The ZOO `Buffer` scenario under
[`../results/maps/zoo-local/geojson-value`](../results/maps/zoo-local/geojson-value/)
provides another successful linked GeoJSON Polygon without copying that
scenario into this directory.

## Validation and provider-failure examples

| Scenario | Why it is separate |
|---|---|
| [`validation/directed-local/undocumented-array-length`](validation/directed-local/undocumented-array-length/) | The schema does not state the required array length |
| [`validation/zoo-local/advertised-repeated-raster`](validation/zoo-local/advertised-repeated-raster/) | The description allows a repeated mixed link/inline raster input, but ZOO crashes |
| [`validation/zoo-local/dotted-input-identifiers`](validation/zoo-local/dotted-input-identifiers/) | Input IDs containing dots must remain flat keys; the OTB runtime is unavailable |
| [`validation/zoo-local/inline-las-point-cloud`](validation/zoo-local/inline-las-point-cloud/) | A schema-valid inline LAS file reaches the provider but processing crashes |

These requests remain useful form and serialization fixtures. They are not
successful live-execution examples.

## What matters for the MapLibre UI

The following differences require distinct front-end examples:

- **Ordinary JSON versus GeoJSON.** Only values identified as GeoJSON should
  automatically become a MapLibre GeoJSON source.
- **Geometry versus FeatureCollection.** A Geometry is one shape. A
  FeatureCollection can contain several features and properties that must be
  retained.
- **Point, line and polygon shapes.** They use the same GeoJSON request wrapper
  but need different drawing controls and visual styles. MultiPoint,
  MultiLineString and MultiPolygon must also remain distinct when encountered.
- **Bounding boxes.** A bbox is not GeoJSON. It can use a rectangle control,
  but its coordinate count and CRS must be preserved.
- **Inline value versus URL.** Inline GeoJSON can be previewed immediately. A
  linked value can only be previewed if the browser may fetch it and its media
  type can be parsed.
- **Single versus repeated input.** A repeated geometry or file input needs an
  add/remove control and stable item ordering.
- **CRS and coordinate dimensions.** MapLibre displays longitude/latitude
  GeoJSON. Other CRSs need an explicit transformation. A third coordinate
  should be preserved even when the map view is two-dimensional.

GML, KML, AAIGrid, GeoTIFF and LAS are not direct MapLibre GeoJSON sources.
Unless the application adds a parser or conversion library, their generated
control should be a file or URL input with metadata, not a promised map
preview. CSV should only be mapped when a known schema identifies its spatial
columns.

## From a form answer to an execution request

There are three separate layers:

```text
execute request → input ID → encoded semantic value
```

The execute request always has an `inputs` object. Each input ID from the
process description becomes a property directly inside that object:

```json
{
  "inputs": {
    "<input ID from the process description>": "<encoded user answer>"
  }
}
```

There is no general `variables` or `parameters` level. Such a level exists
only if the process description declares an input with that ID or declares it
as part of an object-valued input.

The process description tells the form which input IDs exist and describes
the semantic value expected for each input. The execution-request rules then
determine whether that value is direct, qualified, referenced, repeated, or a
bounding box.

| Description and user answer | Location in the request |
|---|---|
| Scalar input `distance` with answer `10` | `inputs.distance` |
| Input ID `filter.meanshift.maxiter` | `inputs["filter.meanshift.maxiter"]` |
| Object input `settings` | `inputs.settings.value` |
| Property `threshold` inside `settings` | `inputs.settings.value.threshold` |
| Bounding-box input `area` | `inputs.area.bbox` and `inputs.area.crs` |
| Referenced input `polygon` | `inputs.polygon.href` and `inputs.polygon.type` |
| Repeated input `images` | `inputs.images[0]`, `inputs.images[1]`, and so on |

### Direct values

Primitive values are placed directly under their advertised input ID:

```json
{
  "inputs": {
    "distance": 10,
    "keep_original_type": true
  }
}
```

Input IDs are opaque strings. A dot in an ID does not create another object:

```json
{
  "inputs": {
    "filter.meanshift.maxiter": 100
  }
}
```

### Object-valued inputs

An inline object is a qualified value. The semantic object containing the
user's answers goes under `value`. For example, Weaver describes an input
called `complexObjectInput` with properties including `property1` and
`property5`:

```json
{
  "inputs": {
    "complexObjectInput": {
      "value": {
        "property1": "abc",
        "property5": true
      },
      "mediaType": "application/json"
    }
  }
}
```

The form fields therefore write to
`inputs.complexObjectInput.value.property1` and
`inputs.complexObjectInput.value.property5`. GeoJSON Geometry and
FeatureCollection objects use the same `value` wrapper in the captured Weaver
request.

If a process described an object input called `variables` with a property
called `var1`, the standard qualified form would be:

```json
{
  "inputs": {
    "variables": {
      "value": {
        "var1": "the user answer"
      },
      "mediaType": "application/json"
    }
  }
}
```

The client must not invent `variables` when the description does not declare
it.

### References and bounding boxes

Referenced data uses a link object directly under the input ID:

```json
{
  "inputs": {
    "polygon": {
      "href": "https://example.com/polygon.geojson",
      "type": "application/json"
    }
  }
}
```

A bounding box uses the standard `bbox` and optional `crs` properties directly
under its input ID. Its coordinate array is not wrapped in `value`.

### Repeated inputs and array values

Repeated inputs are arrays under the input ID. Each array entry retains its
own inline or reference wrapper. The captured repeated-raster request contains
one link and one inline value:

```json
{
  "inputs": {
    "INPUT": [
      {
        "href": "https://example.com/dem.asc",
        "type": "application/x-ogc-aaigrid"
      },
      {
        "value": "<base64>",
        "format": {
          "mediaType": "application/x-ogc-aaigrid",
          "encoding": "base64"
        }
      }
    ]
  }
}
```

A semantic array can look identical at this level. For example,
`"intensity": [0, 30, 80]` is one array-valued answer, not three occurrences
of an input. The client must use the input schema and occurrence constraints
from the process description to distinguish these cases. If the description
does not make the distinction clear, the client cannot safely infer it.

### Qualified-value differences in the evidence

The OGC API Processes qualified-value form places format information beside
`value`. Weaver follows that form:

```json
{
  "image": {
    "value": "<base64>",
    "mediaType": "image/tiff; application=geotiff",
    "encoding": "base64"
  }
}
```

The captured ZOO requests instead place the same information inside a nested
`format` object:

```json
{
  "table": {
    "value": "id,name\n1,Alkmaar\n",
    "format": {
      "mediaType": "text/csv",
      "encoding": "utf-8"
    }
  }
}
```

This ZOO request shape is provider behaviour found in the evidence. It cannot
be inferred from an ordinary semantic input schema alone. The client should
use the standard qualified-value form by default; any ZOO compatibility rule
must be based on tested provider behaviour rather than guessed from an input
name.

The rules above come from the
[OGC API Processes Core execute-request requirements](https://docs.ogc.org/is/18-062r2/18-062r2.html#toc53).

### Coverage in this repository

| Placement or encoding | Captured scenario |
|---|---|
| Direct scalar values | [`inputs/bgt-prototype/numeric-ranges`](inputs/bgt-prototype/numeric-ranges/) |
| Flat input IDs containing dots | [`validation/zoo-local/dotted-input-identifiers`](validation/zoo-local/dotted-input-identifiers/) |
| Qualified ordinary JSON object | [`inputs/weaver-local/mixed-values-map-and-files`](inputs/weaver-local/mixed-values-map-and-files/) |
| Qualified GeoJSON Geometry and FeatureCollection | [`inputs/weaver-local/mixed-values-map-and-files`](inputs/weaver-local/mixed-values-map-and-files/) |
| Bounding box with CRS | [`inputs/weaver-local/mixed-values-map-and-files`](inputs/weaver-local/mixed-values-map-and-files/) |
| Referenced GeoJSON, GML, and raster values | [`inputs/zoo-local`](inputs/zoo-local/) |
| Repeated qualified values | [`inputs/weaver-local/mixed-values-map-and-files`](inputs/weaver-local/mixed-values-map-and-files/) |
| Semantic array value | [`validation/directed-local/undocumented-array-length`](validation/directed-local/undocumented-array-length/) |
| Mixed referenced and inline occurrences | [`validation/zoo-local/advertised-repeated-raster`](validation/zoo-local/advertised-repeated-raster/) |

The scenarios capture the main placement rules. The repository still lacks a
deeply nested ordinary JSON input and a successful mixed reference/inline
repeated input.

## Important findings

- `application/json` can mean ordinary JSON, a GeoJSON Geometry, or a GeoJSON
  FeatureCollection. Use `contentSchema`, schema format, and advertised media
  types together. If those do not identify GeoJSON, use raw JSON.
- Providers do not consistently use `application/geo+json` for GeoJSON.
- Descriptive input names such as `POINTS` or `POLYGONS` are useful labels but
  are not a reliable machine-readable geometry constraint.
- A server-side filename is not a browser file upload. The GDAL path examples
  remain provider evidence rather than form scenarios.
- If input matches the description and the provider fails, show the provider
  error. Do not rewrite the request or claim the form value was invalid.

## Input coverage still missing

The repository still lacks captured form inputs for:

- MultiPoint, MultiLineString, MultiPolygon and GeometryCollection values;
- a mixed-geometry FeatureCollection;
- a six-coordinate, three-dimensional bounding box;
- a deeply nested ordinary JSON value unrelated to GeoJSON coordinates;
- a successful LAS point-cloud execution;
- successful KML, NetCDF or Metalink inputs;
- a successful linked complex input from a provider other than ZOO;
- non-WGS84 spatial input with enough CRS information for safe preview.

Weaver `EchoProcess` advertises general GeoJSON geometry and bounding-box
inputs. It is the best current candidate for capturing the missing GeoJSON
shapes and three-dimensional bbox without adding another process.
