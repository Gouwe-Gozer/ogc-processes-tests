# Case inventory

Every selected protocol/basic, GDAL/OGR/GEOS/CGAL, and SAGA process has an
initial case. A `ready` case contains an exact `request.json`. Public complex
inputs are pinned to an immutable repository commit; newly added SAGA fixtures
are embedded inline until they are published. A `pending` case records its
intended fixture and expected outcome but deliberately omits the request until
the remaining server-side delivery detail is known.

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

## SAGA cases

HTTP 200 alone is not labelled `ready` when the requested result is missing or
its reference is unusable. Exact response bodies are preserved in
`evidence/zoo/`; see `SAGA_EXECUTION_OBSERVATIONS.md` for the full matrix.

| Process | Primary case | Observed status | Additional evidence |
|---|---|---|---|
| `SAGA.grid_tools.0` | `saga_resample_rasters` | ready | Two repeated `INPUT` values return 500 `SIGSEGV` |
| `SAGA.grid_tools.3` | `saga_mosaic_rasters` | ready | Two repeated `GRIDS` values return 500 `SIGSEGV` |
| `SAGA.grid_tools.27` | `saga_tile_raster` | incomplete result | HTTP 200 with `{}` instead of requested tiles |
| `SAGA.grid_calculus.1` | `saga_grid_calculator` | ready | Two repeated `GRIDS` values return 500 `SIGSEGV` |
| `SAGA.grid_filter.1` | `saga_gaussian_filter` | ready | — |
| `SAGA.grid_gridding.1` | `saga_idw_points` | expected error | HTTP 500 `SIGSEGV`, also with optional controls omitted |
| `SAGA.shapes_grid.5` | `saga_contours_raster` | ready | — |
| `SAGA.shapes_grid.0` | `saga_add_grid_values_points` | ready | — |
| `SAGA.shapes_polygons.5` | `saga_dissolve_polygons` | incomplete result | HTTP 200 with `{}` instead of requested result |
| `SAGA.shapes_polygons.14` | `saga_intersect_polygons` | expected error | HTTP 500 `SIGABRT`, also with optional controls omitted |
| `SAGA.shapes_points.16` | `saga_thiessen_points` | expected error | HTTP 500 `SIGABRT`, also with optional controls omitted |
| `SAGA.shapes_lines.3` | `saga_line_polygon_intersection` | ready | — |
| `SAGA.table_tools.0` | `saga_create_table` | invalid result reference | HTTP 200 advertises a TIFF URL, but no TIFF is created |
| `SAGA.table_tools.3` | `saga_join_tables` | ready | — |
| `SAGA.tin_tools.2` | `saga_shapes_to_tin` | ready | Five inline GeoJSON outputs |
| `SAGA.tin_tools.3` | `saga_tin_to_shapes` | ready | Five inline GeoJSON outputs |
| `SAGA.pointcloud_tools.4` | `saga_pointcloud_to_grid` | expected error | HTTP 500 `SIGSEGV`, also with optional controls omitted |
| `SAGA.statistics_grid.5` | `saga_zonal_statistics` | ready | Inline CSV output |

The older `Gdal_*` and `Ogr2Ogr` descriptions expose source and destination as
literal filename strings. For the local Docker profile, stage fixtures with:

```bash
python3 scripts/stage_zoo_fixtures.py
```

This copies `fixtures/` below `/usr/com/zoo-project/ogc-processes-tests/`, the
configured ZOO `dataPath`. Provider outputs use the configured `/tmp/zTmp`.
