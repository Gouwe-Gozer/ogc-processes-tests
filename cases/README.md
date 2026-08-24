# Case inventory

Every selected protocol/basic and GDAL/OGR/GEOS/CGAL process has one initial
case. A `ready` case contains an exact `request.json`. Public complex inputs are
pinned to an immutable repository commit. A `pending` case records its intended
fixture and expected outcome but deliberately omits the request until the
remaining server-side delivery detail is known.

The runner returns exit code `3` for pending cases.

| Process | Case | Status | Remaining work |
|---|---|---|---|
| `hellojs` | `hellojs_string` | ready | — |
| `EchoProcess` | `echo_all_input_kinds` | ready | — |
| `longProcess` | `long_process_async` | ready | Polling and dismissal are future cases |
| `demo` | `demo_async_expected_failure` | ready | Poll the created job to assert its eventual failure |
| `failR` | `fail_r_expected_error` | ready | — |
| `Gdal_Translate` | `gdal_translate_raster` | pending | Stage input and choose a writable server output path |
| `Gdal_Warp` | `gdal_warp_raster` | pending | Stage input and choose a writable server output path |
| `Gdal_Dem` | `gdal_dem_hillshade` | pending | Stage input and choose a writable server output path |
| `Gdal_Contour` | `gdal_contour_dem` | pending | Stage input and choose a writable server output path |
| `Gdal_Grid` | `gdal_grid_points` | pending | Stage input and choose a writable server output path |
| `GdalExtractProfile` | `gdal_extract_profile_line` | pending | Stage the DEM under ZOO `dataPath` |
| `Ogr2Ogr` | `ogr2ogr_vector` | pending | Stage input and choose a writable server output path |
| `Buffer` | `buffer_polygon` | ready | — |
| `Centroid` | `centroid_polygon` | ready | — |
| `Boundary` | `boundary_polygon` | ready | — |
| `ConvexHull` | `convex_hull_polygon` | ready | — |
| `Simplify` | `simplify_polygon` | ready | — |
| `Intersection` | `intersection_polygons` | ready | — |
| `Union` | `union_polygons` | ready | — |
| `Difference` | `difference_polygons` | ready | — |
| `SymDifference` | `symmetric_difference_polygons` | ready | — |
| `Distance` | `distance_polygons` | ready | Provider accepts polygon GML but rejects point GML despite generic wording |
| `GetArea` | `get_area_polygon` | ready | — |
| `Contains` | `contains_polygon_point` | ready | — |
| `IsValid` | `is_valid_polygon` | ready | — |
| `Delaunay` | `delaunay_five_points` | ready | — |

The older `Gdal_*` and `Ogr2Ogr` descriptions expose source and destination as
literal filename strings. A GitHub URL must not be substituted unless live
execution proves the provider accepts it as a data source.
