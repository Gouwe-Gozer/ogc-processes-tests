# One advertised process description returns non-JSON HTTP 500

Process: `OTB.ReadImageInfo`
Source server: `zoo-local`

The process-description endpoint returns HTML with HTTP 500 even though the
request asks for JSON.

The protocol core should keep other discovered processes usable and mark only
this description as unavailable. It should retain the status, headers, final
URL, and raw body without rendering the HTML as trusted application markup.
