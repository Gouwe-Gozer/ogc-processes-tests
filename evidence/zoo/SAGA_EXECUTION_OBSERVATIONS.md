# SAGA execution observations

The 18 selected SAGA process descriptions and primary cases were exercised
synchronously against local profile `zoo-ubuntu18-gdal3-saga7-otb7` on
2026-08-25. A matching `*.process.json` records the advertised contract; the
linked execution file records the raw response body.

| Process | HTTP | Result assessment | Execution evidence |
|---|---:|---|---|
| `SAGA.grid_tools.0` | 200 | usable referenced TIFF from one raster | [`SAGA.grid_tools.0.execution.json`](SAGA.grid_tools.0.execution.json) |
| `SAGA.grid_tools.3` | 200 | usable referenced TIFF from one raster | [`SAGA.grid_tools.3.execution.json`](SAGA.grid_tools.3.execution.json) |
| `SAGA.grid_tools.27` | 200 | empty `{}`; requested repeated `TILES` output missing | [`SAGA.grid_tools.27.execution.json`](SAGA.grid_tools.27.execution.json) |
| `SAGA.grid_calculus.1` | 200 | usable referenced TIFF from one raster | [`SAGA.grid_calculus.1.execution.json`](SAGA.grid_calculus.1.execution.json) |
| `SAGA.grid_filter.1` | 200 | usable referenced TIFF | [`SAGA.grid_filter.1.execution.json`](SAGA.grid_filter.1.execution.json) |
| `SAGA.grid_gridding.1` | 500 | provider `SIGSEGV` | [`SAGA.grid_gridding.1.execution-error.json`](SAGA.grid_gridding.1.execution-error.json) |
| `SAGA.shapes_grid.5` | 200 | contour and polygon GeoJSON values | [`SAGA.shapes_grid.5.execution.json`](SAGA.shapes_grid.5.execution.json) |
| `SAGA.shapes_grid.0` | 200 | points enriched with sampled grid value | [`SAGA.shapes_grid.0.execution.json`](SAGA.shapes_grid.0.execution.json) |
| `SAGA.shapes_polygons.5` | 200 | empty `{}`; requested `DISSOLVED` output missing | [`SAGA.shapes_polygons.5.execution.json`](SAGA.shapes_polygons.5.execution.json) |
| `SAGA.shapes_polygons.14` | 500 | provider `SIGABRT` | [`SAGA.shapes_polygons.14.execution-error.json`](SAGA.shapes_polygons.14.execution-error.json) |
| `SAGA.shapes_points.16` | 500 | provider `SIGABRT` | [`SAGA.shapes_points.16.execution-error.json`](SAGA.shapes_points.16.execution-error.json) |
| `SAGA.shapes_lines.3` | 200 | intersection and difference GeoJSON values | [`SAGA.shapes_lines.3.execution.json`](SAGA.shapes_lines.3.execution.json) |
| `SAGA.table_tools.0` | 200 | unusable TIFF reference; target file absent | [`SAGA.table_tools.0.execution.json`](SAGA.table_tools.0.execution.json) |
| `SAGA.table_tools.3` | 200 | joined CSV value | [`SAGA.table_tools.3.execution.json`](SAGA.table_tools.3.execution.json) |
| `SAGA.tin_tools.2` | 200 | five GeoJSON TIN-related values | [`SAGA.tin_tools.2.execution.json`](SAGA.tin_tools.2.execution.json) |
| `SAGA.tin_tools.3` | 200 | five GeoJSON values | [`SAGA.tin_tools.3.execution.json`](SAGA.tin_tools.3.execution.json) |
| `SAGA.pointcloud_tools.4` | 500 | provider `SIGSEGV` | [`SAGA.pointcloud_tools.4.execution-error.json`](SAGA.pointcloud_tools.4.execution-error.json) |
| `SAGA.statistics_grid.5` | 200 | three-zone CSV statistics value | [`SAGA.statistics_grid.5.execution.json`](SAGA.statistics_grid.5.execution.json) |

Fourteen primary requests returned HTTP 200. Eleven delivered a usable result;
two omitted the requested output and one returned a reference to a file that
was not created. Four primary requests returned HTTP 500 after a provider
signal. Removing optional inputs from those four did not change the outcome.

In addition, the three raster processes that succeed with one input terminate
with `SIGSEGV` when supplied two values through their advertised repeated
input. Those exact negative requests and responses are indexed in
[`SAGA_FAILURES.md`](SAGA_FAILURES.md).
