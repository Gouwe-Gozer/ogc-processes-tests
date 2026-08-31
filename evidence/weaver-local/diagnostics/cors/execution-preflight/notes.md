# Local Weaver execution preflight

Captured on 31 August 2026 for browser origin `http://localhost:5173`.

Browser verdict: **blocked**.

The endpoint returned HTTP 405 because `OPTIONS` is not allowed and supplied
no CORS permission headers. A browser cannot send the cross-origin JSON POST
directly. The client needs the promised relay transport for this deployment.
