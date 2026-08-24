# Case inventory

Every selected protocol/basic and GDAL/OGR/GEOS/CGAL process has one initial
case. A `ready` case contains an exact `request.json`. A `pending` case records
its intended fixture and expected outcome but deliberately omits the request
until the remaining delivery detail is known.

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
| `Buffer` | `buffer_polygon` | pending | Publish or inline the fixture and select a small distance |
| `Centroid` | `centroid_polygon` | pending | Publish or inline the GML fixture |
| `Boundary` | `boundary_polygon` | pending | Publish or inline the GML fixture |
| `ConvexHull` | `convex_hull_polygon` | pending | Publish or inline the GML fixture |
| `Simplify` | `simplify_polygon` | pending | Publish or inline the fixture and select a small tolerance |
| `Intersection` | `intersection_polygons` | pending | Publish or inline two GML fixtures |
| `Union` | `union_polygons` | pending | Publish or inline two GML fixtures |
| `Difference` | `difference_polygons` | pending | Publish or inline two ordered GML fixtures |
| `SymDifference` | `symmetric_difference_polygons` | pending | Publish or inline two GML fixtures |
| `Distance` | `distance_points` | pending | Publish or inline two GML fixtures |
| `GetArea` | `get_area_polygon` | pending | Publish or inline the GML fixture |
| `Contains` | `contains_polygon_point` | pending | Publish or inline polygon and point GML fixtures |
| `IsValid` | `is_valid_polygon` | pending | Publish or inline the GML fixture |
| `Delaunay` | `delaunay_five_points` | pending | Publish or inline the GML fixture |

The older `Gdal_*` and `Ogr2Ogr` descriptions expose source and destination as
literal filename strings. A GitHub URL must not be substituted unless live
execution proves the provider accepts it as a data source.
