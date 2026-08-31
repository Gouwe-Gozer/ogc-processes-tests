# DIRECTED discovery

Source server: `directed-local`

This capture contains the landing page, conformance declaration, and process
list returned by the local DIRECTED deployment on 31 August 2026. The service
exposes one process: `climada-simple-example-denmark-process`.

The process supports synchronous and asynchronous execution. The landing page
advertises the global jobs resource.

The service returns `Access-Control-Allow-Origin` for the requesting browser
origin and exposes its response headers, so this local deployment can be called
directly from that origin.
