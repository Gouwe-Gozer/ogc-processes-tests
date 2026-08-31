# Public pygeoapi demo discovery

Source server: `pygeoapi-demo`

This capture contains the landing page, conformance declaration, and process
list returned by the public stable pygeoapi demo on 31 August 2026. This stable
deployment exposes one process: `hello-world`.

The process advertises synchronous and asynchronous execution. The landing
page does not advertise a global jobs link and the conformance response does
not declare the job-list class, although `GET /jobs` is available.

The service returns `Access-Control-Allow-Origin: *` and exposes its response
headers, so a browser can read these discovery GETs directly. Its execution
preflight does not allow the required `content-type` and `prefer` request
headers; execution therefore still requires a relay. See
[`../../../diagnostics/cors/execution-preflight/`](../../../diagnostics/cors/execution-preflight/).
