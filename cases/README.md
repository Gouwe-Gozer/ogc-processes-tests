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
| `Gdal_Translate` | `gdal_translate_raster` | ready | Requires local fixture staging |
| `Gdal_Warp` | `gdal_warp_raster` | ready | Requires local fixture staging |
| `Gdal_Dem` | `gdal_dem_slope` | ready | Requires local fixture staging; hillshade needs an unadvertised input |
| `Gdal_Contour` | `gdal_contour_dem` | ready | Requires local fixture staging |
| `Gdal_Grid` | `gdal_grid_points` | expected error | Provider needs unadvertised parameters and returns 500 |
| `GdalExtractProfile` | `gdal_extract_profile_line` | ready | Requires local fixture staging |
| `Ogr2Ogr` | `ogr2ogr_vector` | ready | Requires local fixture staging |
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
literal filename strings. For the local Docker profile, stage fixtures with:

```bash
python3 scripts/stage_zoo_fixtures.py
```

This copies `fixtures/` below `/usr/com/zoo-project/ogc-processes-tests/`, the
configured ZOO `dataPath`. Provider outputs use the configured `/tmp/zTmp`.
