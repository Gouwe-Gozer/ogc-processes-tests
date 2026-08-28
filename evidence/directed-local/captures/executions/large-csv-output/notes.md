# Large CLIMADA CSV output

Process: `climada-simple-example-denmark-process`
Source server: `directed-local`

The developers' example request completed synchronously with HTTP 200. Despite
`Accept: application/json`, the server correctly identified the actual raw body
as `text/csv`. It also returned an exposed `Location` header for the completed
job.

The CSV contains 328,321 lines and is about 18.8 MB, so it is not stored in
this repository. The observation file records its exact size, hash, media type,
and header row without presenting a shortened body as a complete response.

A second request asked for document mode with the `impact` output transmitted
by reference. The server instead returned HTTP 200 JSON containing an
`outputs` array with the entire CSV as one string. That 19.5 MB response is
also represented by measured metadata rather than a checked-in body.

Client relevance:

- use the response `Content-Type` when selecting result handling;
- do not parse a `text/csv` body as JSON merely because the request accepted
  JSON;
- remain able to handle an inline value when a requested reference is not
  supplied;
- expose large CSV results as a download instead of rendering the complete
  body in the page.
