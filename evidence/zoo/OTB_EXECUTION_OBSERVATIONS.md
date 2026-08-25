# OTB execution observations

The six required OTB error and schema processes were tested against local profile
`zoo-ubuntu18-gdal3-saga7-otb7` on 2026-08-25.

Five process descriptions return HTTP 200 and have exact execution requests.
Every execution reaches the ZOO OTB adapter but returns the same HTTP 500
problem before request data is processed:

```json
{"title":"InternalError","type":"InternalError","detail":"No OTB Application found."}
```

The container has OTB 7.0 CLI applications and the application modules below
`/usr/lib/x86_64-linux-gnu/otb/applications`, but the ZOO process environment
does not expose `ITK_AUTOLOAD_PATH` or another OTB application path. ZOO's
adapter sees an empty `ApplicationRegistry`. This is consistent with runtime
environment configuration, not invalid fixture data. It remains a server-side
integration finding; a client must not attempt to repair it.

| Process | Description | API execution | Direct OTB 7 CLI validation | Response evidence |
|---|---:|---|---|---|
| `OTB.PixelValue` | 200 | 500 `InternalError` | succeeds; pixel value is `[3]` | [`OTB.PixelValue.execution-error.json`](OTB.PixelValue.execution-error.json) |
| `OTB.BandMath` | 200 | 500 `InternalError` | succeeds with two images and `im1b1 + im2b1` | [`OTB.BandMath.execution-error.json`](OTB.BandMath.execution-error.json) |
| `OTB.Rasterization` | 200 | 500 `InternalError` | succeeds with GeoJSON and the support GeoTIFF | [`OTB.Rasterization.execution-error.json`](OTB.Rasterization.execution-error.json) |
| `OTB.ComputeImagesStatistics` | 200 | 500 `InternalError` | succeeds with two images and XML output | [`OTB.ComputeImagesStatistics.execution-error.json`](OTB.ComputeImagesStatistics.execution-error.json) |
| `OTB.Segmentation` | 200 | 500 `InternalError` | succeeds in raster mean-shift mode | [`OTB.Segmentation.execution-error.json`](OTB.Segmentation.execution-error.json) |
| `OTB.ReadImageInfo` | 500 | not constructible from a description | succeeds; reports one float band and a 5-by-5 image | [`OTB.ReadImageInfo.process-error.html`](OTB.ReadImageInfo.process-error.html) |

## Description particularities retained in the cases

- `BandMath` and `ComputeImagesStatistics` advertise image lists with
  `maxOccurs: 1024`; their requests use two inline base64 images.
- `BandMath`, `Rasterization`, and raster-mode `Segmentation` use the output ID
  as an input selecting output pixel type and again as the requested output ID.
  Input and output namespaces must therefore remain distinct.
- `Rasterization` marks inputs for both binary and attribute modes as required.
  The request includes both while selecting binary mode.
- `Segmentation` exposes dotted conditional parameter IDs and marks parameters
  from inactive filter and vector branches as required. The request preserves
  all required advertised values while selecting raster mean-shift mode.
- `ReadImageInfo` returns generic Apache HTML rather than an OGC JSON problem.
  The server log records `zoo_loader.cgi` terminating with `SIGSEGV`.

The GeoTIFF fixture is only 5 by 5 pixels. Successful direct CLI runs for all
six applications establish
that it is readable by the installed OTB build and that each chosen parameter
set is viable. They do not turn the CLI into part of the API test contract; the
canonical API results remain expected HTTP 500 for this profile.

The direct checks are also recorded in machine-readable form in
[`OTB.direct-cli-validation.json`](OTB.direct-cli-validation.json).
