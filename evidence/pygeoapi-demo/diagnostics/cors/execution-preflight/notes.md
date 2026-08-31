# Public pygeoapi demo execution preflight

Captured on 31 August 2026 for browser origin `http://localhost:5173`.

Browser verdict: **blocked**.

The response allows any origin and includes POST in the allowed methods, but it
only allows the `Authorization` request header. It does not allow the requested
`content-type` or `prefer` headers. A browser therefore rejects this preflight
and does not send the JSON execution POST.
