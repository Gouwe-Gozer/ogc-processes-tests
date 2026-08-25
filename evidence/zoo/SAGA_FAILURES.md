# SAGA failure evidence

These requests were executed synchronously against the local
`zoo-ubuntu18-gdal3-saga7-otb7` profile on 2026-08-25. Each request is retained
as a runnable case whose expected status is HTTP 500. The JSON evidence file
contains the problem document returned by ZOO.

| Process | Request shape | HTTP | Provider signal | Runnable case | Response evidence |
|---|---|---:|---|---|---|
| `SAGA.grid_tools.0` | two advertised `INPUT` raster values | 500 | `SIGSEGV` | [`saga_resample_rasters_repeated_input_expected_error`](../../cases/saga_resample_rasters_repeated_input_expected_error/) | [`SAGA.grid_tools.0.repeated-input.execution-error.json`](SAGA.grid_tools.0.repeated-input.execution-error.json) |
| `SAGA.grid_tools.3` | two advertised `GRIDS` raster values | 500 | `SIGSEGV` | [`saga_mosaic_rasters_repeated_input_expected_error`](../../cases/saga_mosaic_rasters_repeated_input_expected_error/) | [`SAGA.grid_tools.3.repeated-input.execution-error.json`](SAGA.grid_tools.3.repeated-input.execution-error.json) |
| `SAGA.grid_calculus.1` | two advertised `GRIDS` raster values | 500 | `SIGSEGV` | [`saga_grid_calculator_repeated_input_expected_error`](../../cases/saga_grid_calculator_repeated_input_expected_error/) | [`SAGA.grid_calculus.1.repeated-input.execution-error.json`](SAGA.grid_calculus.1.repeated-input.execution-error.json) |
| `SAGA.grid_gridding.1` | GeoJSON 3D points and user grid | 500 | `SIGSEGV` | [`saga_idw_points`](../../cases/saga_idw_points/) | [`SAGA.grid_gridding.1.execution-error.json`](SAGA.grid_gridding.1.execution-error.json) |
| `SAGA.shapes_polygons.14` | two GeoJSON polygon layers | 500 | `SIGABRT` | [`saga_intersect_polygons`](../../cases/saga_intersect_polygons/) | [`SAGA.shapes_polygons.14.execution-error.json`](SAGA.shapes_polygons.14.execution-error.json) |
| `SAGA.pointcloud_tools.4` | inline base64 LAS 1.2 | 500 | `SIGSEGV` | [`saga_pointcloud_to_grid`](../../cases/saga_pointcloud_to_grid/) | [`SAGA.pointcloud_tools.4.execution-error.json`](SAGA.pointcloud_tools.4.execution-error.json) |
| `SAGA.shapes_points.16` | referenced GeoJSON points | 500 | `SIGABRT` | [`saga_thiessen_points`](../../cases/saga_thiessen_points/) | [`SAGA.shapes_points.16.execution-error.json`](SAGA.shapes_points.16.execution-error.json) |

The three repeated-raster failures also have a successful single-raster case.
That distinction shows that the process itself is reachable but the advertised
multi-value input path fails in this provider build.
