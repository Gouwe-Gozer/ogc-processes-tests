# Possible ZOO-Project issues from recorded API interactions

We collected these requests and responses while testing interoperability with
OGC API Processes clients. Four observations may be useful to ZOO maintainers.
Each includes the original evidence; responsibility may lie in ZOO, a provider
binding, or our deployment configuration.

## Environment and scope

The [capture notes](README.md) record Ubuntu 18.04.6, GDAL 3.0.4,
SAGA 7.3.0 and OTB 7.x (ZOO adapter configured for 7.0). Execution captures
are documented as 25 August 2026; the CORS capture is dated 31 August 2026.
The source checkout was inspected on 25 September 2026. It is the
[Gouwe-Gozer/ZOO-Project fork](https://github.com/Gouwe-Gozer/ZOO-Project),
with a clean working tree at commit
[`79014a595f22fbcfafa0f259884b9037e56269a3`](https://github.com/Gouwe-Gozer/ZOO-Project/commit/79014a595f22fbcfafa0f259884b9037e56269a3)
(28 August 2026).

- **Declared kernel version: 2.1.0**, from
  [`configure.ac`](https://github.com/Gouwe-Gozer/ZOO-Project/blob/79014a595f22fbcfafa0f259884b9037e56269a3/zoo-project/zoo-kernel/configure.ac#L1).
  `git describe --tags --always` reports `rel-2.1.0-55-g79014a5`.
  This is a modified post-tag checkout, not an unmodified 2.1.0 release.
- **Upstream ancestry:** the merge base with the locally available
  `upstream/main` reference is
  [`19f3c4eed7c9ec9d1f0375bbe59f9d204a42bd3a`](https://github.com/ZOO-Project/ZOO-project/commit/19f3c4eed7c9ec9d1f0375bbe59f9d204a42bd3a).
  The checkout contains seven subsequent fork commits. No remote fetch was
  performed, so this does not identify today's upstream HEAD.
- **Local changes:** these include a kernel response-printing fix
  ([`1d0ff4c`](https://github.com/Gouwe-Gozer/ZOO-Project/commit/1d0ff4cc9e8421aea52ec4ddb422334a9cbed5f9)),
  building patched executables, correcting asynchronous worker startup, and
  bundling local providers. These differences matter when comparing with upstream.
- **Build configuration:**
  [`docker/zookernel-local.Dockerfile`](https://github.com/Gouwe-Gozer/ZOO-Project/blob/79014a595f22fbcfafa0f259884b9037e56269a3/docker/zookernel-local.Dockerfile)
  defaults to base image
  `zooproject/zoo-project@sha256:4a50c0b9801677a43a8483abf9e84a1c906dec698c07914852003d357b79b417`.
  It builds the kernel from checkout source and copies the resulting executables
  and selected providers into the runtime image. Compose configures both
  `zookernel` and `zoofpm` to use `zoo-project:local`.

**Deployment provenance (confirmed by the deployment owner):** the image used
for these captures was not updated, and matches the fork's source/build setup
identified above. The owner also confirmed that the checkout changes after the
25 August captures did not affect the image. The findings therefore concern
this locally built ZOO Kernel 2.1.0-based fork, including its local patches.
The checkout revision above identifies the inspected source context; it is not
claimed as a recorded image build revision.

This deployment history is owner-confirmed. Docker was unavailable during
inspection, so the final local image ID was not independently read. The pinned
base-image digest above identifies the base, not the final locally built image.
These observations have not been rechecked against current upstream ZOO.

## 1. Repeated raster input returns SIGSEGV

**Request:** `POST /processes/SAGA.grid_tools.0/execution`.
The process description advertises up to 1,024 `INPUT` values. A single linked
raster succeeds. A request containing two raster inputs, one linked AAIGrid
and one inline base64 AAIGrid, returns HTTP 500 with:

```text
ZOO Kernel failed to process your request, receiving signal 11 = SIGSEGV
```

Evidence: [description](captures/descriptions/SAGA.grid_tools.0/response.json),
[single-input request](captures/executions/saga_resample_rasters/request.json),
[single-input response](captures/executions/saga_resample_rasters/response.json),
[failing request](captures/executions/saga_resample_rasters_repeated_input_expected_error/request.json),
[failing response](captures/executions/saga_resample_rasters_repeated_input_expected_error/response.json).

Expected: process supported repeated inputs, or return a useful validation or
processing error without a memory-access crash. The captures do not isolate
whether repetition, inline input, or mixing the two representations triggers
the failure. Comparing two linked inputs with a single inline input would help
narrow it down. The failing request's `expected_status: 500` records the observed
failure for replay; it does not mean a crash is intended behaviour.

## 2. Reading the OTB.ReadImageInfo description returns HTTP 500

**Request:** `GET /processes/OTB.ReadImageInfo` with `Accept: application/json`.
The response is an Apache HTML error page with HTTP 500. No execution or input
file is involved in this GET.

Evidence: [request](captures/descriptions/OTB.ReadImageInfo/request.json),
[response](captures/descriptions/OTB.ReadImageInfo/response.json).

Expected: an available process description should be readable. The original
capture notes attribute the failure to a SIGSEGV in `zoo_loader.cgi`; the HTTP
response itself proves the 500, not its underlying cause. A fresh reproduction
with server logs would be needed to confirm that diagnosis and distinguish a
loader defect from an OTB installation or binding problem.

## 3. Raster tiling returns HTTP 200 with no requested output

**Request:** `POST /processes/SAGA.grid_tools.27/execution`.
The request asks for `TILES` as referenced GeoTIFF output, using a small raster,
3-by-3-cell tiles, zero overlap and `TILES_SAVE: false`. The response is HTTP 200
with an empty JSON object (`{}`).

Evidence: [request](captures/executions/saga_tile_raster/request.json),
[response](captures/executions/saga_tile_raster/response.json),
[description](captures/descriptions/SAGA.grid_tools.27/response.json).

Expected: return the requested tiles, or explain why no output can be produced.
A client has neither output nor an error to present. This is a candidate output
mapping or configuration issue; the capture does not establish whether SAGA
produced tiles internally or whether `TILES_SAVE` affects the binding's handling.

## 4. Preflight says CORS is enabled but omits permission headers

**Request:** `OPTIONS /processes/hellojs/execution`, with origin
`http://localhost:5173`, requested method `POST`, and requested headers
`content-type, prefer`.

The response is HTTP 200 with the text `CORS is enabled.`, but contains none of
`Access-Control-Allow-Origin`, `Access-Control-Allow-Methods` or
`Access-Control-Allow-Headers`. This response does not permit the browser to
send the cross-origin execution request.

Evidence: [request](diagnostics/cors/execution-preflight/request.json),
[response](diagnostics/cors/execution-preflight/response.json).
See also [browser preflight behaviour](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS).

Expected: if this origin and request are meant to be allowed, the preflight
should return the corresponding permission headers. This may be an Apache or
container configuration issue. The evidence does not establish that CORS fails
in other ZOO deployments. Command-line requests and our recorded-response
client tests do not enforce browser CORS, so they can pass despite this problem.

## Reproducing the requests

From this repository's root, print the exact execution request as a curl command:

```bash
python3 scripts/run_evidence_request.py \
  evidence/zoo-local/captures/executions/saga_resample_rasters_repeated_input_expected_error/request.json \
  --server zoo-local --base-url http://localhost/ogc-api --print-curl
```

Replace the request path with another linked execution or description request.
`--print-curl` sends nothing; removing it sends the request and displays the
response without replacing the saved evidence. Execution examples require the
corresponding SAGA processes and access to the linked raster fixtures.

For the CORS check, use curl directly:

```bash
curl -i -X OPTIONS 'http://localhost/ogc-api/processes/hellojs/execution' \
  -H 'Origin: http://localhost:5173' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: content-type, prefer'
```

For follow-up, record the ZOO revision/image digest, provider versions and server
logs alongside any fresh response. The two crash observations are the strongest
starting points; the output and CORS cases need deployment-level investigation.
