# ZOO execution preflight

Captured on 31 August 2026 for browser origin `http://localhost:5173`.

Browser verdict: **blocked**.

The endpoint returned HTTP 200 and the text `CORS is enabled.`, but it did not
return `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, or
`Access-Control-Allow-Headers`. A browser therefore rejects the preflight and
does not send the execution POST.
