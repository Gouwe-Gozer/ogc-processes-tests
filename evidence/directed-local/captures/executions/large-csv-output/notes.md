# Large CLIMADA CSV output

Process: `climada-simple-example-denmark-process`
Source server: `directed-local`

The developers' example request completed synchronously with HTTP 200. Despite
`Accept: application/json`, the server correctly identified the actual raw body
as `text/csv`. It also returned an exposed `Location` header for the completed
job.

The CSV contains 328,321 lines and is about 18.8 MB. The complete body is
stored in `01-execute-raw.body.csv`; `01-execute-raw.response.json` records the
HTTP status, headers, final URL, and the name of that body file.

A second request asked for document mode with the `impact` output transmitted
by reference. The server instead returned HTTP 200 JSON containing an
`outputs` array with the entire CSV as one string. The complete response body
is stored in `02-execute-reference.body.json` and is referenced by
`02-execute-reference.response.json`.

Client relevance:

- use the response `Content-Type` when selecting result handling;
- do not parse a `text/csv` body as JSON merely because the request accepted
  JSON;
- remain able to handle an inline value when a requested reference is not
  supplied;
- expose large CSV results as a download instead of rendering the complete
  body in the page.
