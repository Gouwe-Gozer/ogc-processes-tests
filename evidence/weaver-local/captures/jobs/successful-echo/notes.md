# Successful async job workflow

The request is accepted with HTTP 201. Polling reaches `successful`, and the
results endpoint returns ten outputs. Some values are inline; others are links.

The dynamic job ID, job URL, and output URLs are represented by placeholders in
the stored exchange. At capture time the output links used the separate file
proxy at `http://localhost:8000`.

Following those links produced mixed results:

- the structured JSON object returned HTTP 200, but no `Content-Type` header;
- the GeoJSON geometry, GeoJSON feature collection, and TIFF returned HTTP 403.

A successful job therefore does not guarantee that every referenced result can
be downloaded. The client should report a failed output request separately from
the completed process job.
