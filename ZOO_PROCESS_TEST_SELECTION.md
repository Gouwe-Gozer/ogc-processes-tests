# ZOO-Project process test selection

This document defines a curated backlog of ZOO-Project processes for which this
repository can collect reusable OGC API - Processes calls. It is based on the
703 processes advertised by the local ZOO-Project instance inspected on
2026-08-24.

The selection favours:

- diverse literal, bounding-box, vector, raster, table, TIN and point-cloud
  inputs and outputs;
- inline values as well as referenced inputs and outputs;
- multiple inputs, repeated inputs and multiple outputs;
- synchronous, asynchronous, status, result and failure behaviour;
- a small number of shared runtimes, primarily GDAL/OGR/GEOS and SAGA.

## Status and interpretation

The 44 core entries below now have captured process descriptions and at least
one executable case. This is not a claim that all 44 executions are successful:
the repository deliberately preserves expected errors, empty HTTP-200 results,
and invalid output references alongside usable results. Each case is derived
from its description and keeps the exact request and observed response as
interoperability evidence.

The complete ZOO collection advertises the same capabilities for all 703
entries:

- `sync-execute`, `async-execute` and `dismiss`;
- output transmission by `value` and `reference`.

Consequently, most useful diversity is found in the detailed input/output
schemas and in actual execution behaviour rather than in the collection-level
capability fields.

## Core selection: 44 processes

### Protocol and basic behaviour: 5

| Process ID | Intended coverage |
|---|---|
| `hellojs` | Minimal string input/output baseline; synchronous and asynchronous execution |
| `EchoProcess` | Literal, XML/JSON complex and 2D/3D bounding-box inputs with three matching outputs |
| `longProcess` | Asynchronous job creation, progress polling and completion |
| `demo` | Long-running execution that deliberately ends with an error |
| `failR` | Immediate provider-level failure through the base R runtime |

### GDAL, OGR, GEOS and CGAL: 21

These processes mostly reuse the installed GDAL/OGR/GEOS stack. `Delaunay`
also uses the existing CGAL provider.

| Process ID | Intended coverage |
|---|---|
| `Gdal_Translate` | Defaults, optional values, repeated GCP strings and raster conversion |
| `Gdal_Warp` | CRS values, extents, booleans and many optional parameters |
| `Gdal_Dem` | Different DEM operation modes |
| `Gdal_Contour` | Raster-to-vector workflow |
| `Gdal_Grid` | Vector-to-raster workflow |
| `GdalExtractProfile` | Raster plus GeoJSON geometry to JSON |
| `Ogr2Ogr` | Vector format conversion |
| `Buffer` | Geometry plus numeric distance to geometry |
| `Centroid` | Polygon to point |
| `Boundary` | Polygon to boundary geometry |
| `ConvexHull` | Geometry to polygon |
| `Simplify` | Geometry plus floating-point tolerance |
| `Intersection` | Two complex inputs to complex output |
| `Union` | Two complex inputs to complex output |
| `Difference` | Direction-sensitive binary geometry operation |
| `SymDifference` | Binary geometry operation |
| `Distance` | Two geometries to numeric output |
| `GetArea` | Geometry to numeric output |
| `Contains` | Two geometries to Boolean output |
| `IsValid` | Geometry to Boolean output |
| `Delaunay` | GML input and JSON/GML output alternatives, including UTF-8 and base64 encodings |

The older `Gdal_*` wrappers often describe server-side filenames as string
inputs instead of accepting uploaded complex values. Preserve that distinction
in their cases; do not silently redesign the advertised API in a request
fixture.

### SAGA: 18

These processes reuse the same SAGA installation and collectively provide the
widest input/output diversity in the selection.

| Process ID | Intended coverage |
|---|---|
| `SAGA.grid_tools.0` | Array of up to 1,024 inline or referenced rasters |
| `SAGA.grid_tools.3` | Raster mosaicking, repeated raster inputs and optional file-list input |
| `SAGA.grid_tools.27` | Raster tiling and numeric extent parameters |
| `SAGA.grid_calculus.1` | Raster arrays plus an expression language |
| `SAGA.grid_filter.1` | Raster plus enum, integer and floating-point parameters |
| `SAGA.grid_gridding.1` | Vector-to-raster interpolation with CSV, vector and raster outputs |
| `SAGA.shapes_grid.5` | Raster to contour lines and polygons with two outputs |
| `SAGA.shapes_grid.0` | Vector plus raster array to enriched vector |
| `SAGA.shapes_polygons.5` | Dissolve with field selection and many Boolean options |
| `SAGA.shapes_polygons.14` | Two vector inputs to intersected vector output |
| `SAGA.shapes_points.16` | Point features to Thiessen polygons |
| `SAGA.shapes_lines.3` | Lines plus polygons to intersection and difference outputs |
| `SAGA.table_tools.0` | Literal inputs to table output; includes a known metadata anomaly |
| `SAGA.table_tools.3` | Two CSV tables, field selection and joined CSV output |
| `SAGA.tin_tools.2` | Vector input to five TIN-related outputs |
| `SAGA.tin_tools.3` | TIN input to five vector outputs |
| `SAGA.pointcloud_tools.4` | LAS point cloud to three raster outputs |
| `SAGA.statistics_grid.5` | Raster arrays to CSV zonal statistics |

Known metadata edge cases worth retaining in tests include Boolean schemas
whose enums contain the strings `"true"` and `"false"`, and
`SAGA.table_tools.0` advertising raster media types for a table output. Record
these as observed server metadata; they are not examples of ideal schemas.

## Optional expected-error selection: 6 processes

> **Warning:** these six OTB processes are not currently approved as successful
> execution cases. In the current test environment, developers must treat calls
> to them as **expected-error or pending cases**, not as passing HTTP 200
> examples. Do not add them to a happy-path test run until their OTB execution
> behaviour and fixtures have been validated.

OTB is a substantially heavier optional runtime than the core selection. These
processes are retained because they expose useful client edge cases.

| Process ID | Intended future coverage | Current status |
|---|---|---|
| `OTB.PixelValue` | Raster plus coordinate-mode enum to literal value | Description works; execution must currently be treated as expected-error/pending |
| `OTB.BandMath` | Raster array plus mathematical expression | Description works; execution must currently be treated as expected-error/pending |
| `OTB.Rasterization` | Vector-to-raster with many mixed parameters | Description works; execution must currently be treated as expected-error/pending |
| `OTB.ComputeImagesStatistics` | Up to 1,024 images to XML | Description works; execution must currently be treated as expected-error/pending |
| `OTB.Segmentation` | Conditional raster/vector modes, 27 inputs and two possible outputs | Description works; execution must currently be treated as expected-error/pending |
| `OTB.ReadImageInfo` | Failure handling for a process advertised by the collection | `GET /processes/OTB.ReadImageInfo` currently returns HTTP 500 after `zoo_loader.cgi` receives `SIGSEGV` |

The first five entries have process-description endpoints that return HTTP 200;
the expected-error warning applies to their **execution cases**, which have not
yet been validated as successful. `OTB.ReadImageInfo` is more severely broken:
even its description endpoint currently fails. A client should handle that
failure without crashing, but HTTP 500 is a server defect and must not be
treated as compliant success behaviour.

## Separation of concerns

A process implementation generally does not affect whether a client can list
the collection or parse a valid process description. This makes it possible to
develop discovery and form-generation support before every execution runtime
is installed.

The implementation becomes relevant when testing:

- request validation and actual supported media types;
- synchronous versus asynchronous responses;
- job status, progress, dismissal and result retrieval;
- inline versus referenced outputs;
- multiple and conditional outputs;
- runtime failures, timeouts and invalid server metadata.

For that reason, every eventual case should keep the advertised description,
exact request and observed response together as interoperability evidence.
