# ZOO evidence

The `*.process.json` files are live process descriptions captured from the
local ZOO API on 2026-08-24 for profile
`zoo-ubuntu18-gdal3-saga7-otb7`. All 26 selected description endpoints returned
HTTP 200. `selection.capture.json` records the exact selection.

Notable advertised-contract details:

- the older `Gdal_*` and `Ogr2Ogr` wrappers require server-side source and
  destination filename strings rather than uploaded complex inputs;
- `GdalExtractProfile` similarly interprets `RasterFile` relative to ZOO's
  configured `dataPath`, while its line geometry is JSON complex data;
- most GEOS/CGAL geometry services advertise GML 3.1 only, although `Buffer`
  and `Simplify` additionally advertise JSON;
- `Buffer` and `Simplify` expose the placeholder content-schema host
  `http://fooa/`;
- `Gdal_Warp` describes its `r` resampling-method input as Boolean;
- `EchoProcess` advertises older EPSG URN spellings for bounding-box CRSs.
- `Distance` describes generic geometry inputs, but its provider rejects point
  GML because the implementation extracts only `Polygon` or `MultiPolygon`.

These are captured server facts, not recommendations for ideal process
metadata. Cases must follow the descriptions or clearly record a tested server
extension.

The dated `*.job-*.json` files preserve one observed terminal job state for
the successful `longProcess` and deliberately failing `demo` cases. Their job
identifiers and timestamps are evidence from those individual executions, not
stable values for assertions.
