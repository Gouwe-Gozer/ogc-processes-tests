# BGT prototype discovery

Source server: `bgt-prototype`

This capture contains the landing page, conformance declaration, and process
list returned by the local BGT prototype on 31 August 2026. The service exposes
one process: `bgt-land-cover-summary`.

The process description advertises only `sync-execute`. The landing page also
links to the global jobs resource, but there is no asynchronous process here to
use for a job workflow.

The service returns `Access-Control-Allow-Origin` for the requesting browser
origin, so this local deployment can be called directly from that origin.
