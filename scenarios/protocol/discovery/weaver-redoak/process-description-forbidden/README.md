# Advertised process description is forbidden

Process: `EchoProcess:1.0.0`
Source server: `weaver-redoak`

The Weaver process list advertises this versioned process-description URL, but
following the exact link returns HTTP 403 with an HTML body. The unversioned
description returned the same status during the capture.

The client should keep the process list and its summary available, mark this
description as unavailable, and retain the status and raw response body. It
cannot generate a form for this process without a description.

This is a direct HTTP response, not a browser CORS failure. The source exchange
remains under
[`evidence/weaver-redoak/captures/descriptions/process-description-forbidden/`](../../../../../evidence/weaver-redoak/captures/descriptions/process-description-forbidden/).
