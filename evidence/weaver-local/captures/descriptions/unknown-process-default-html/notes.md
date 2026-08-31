# Unknown process without JSON content negotiation

Without an `Accept: application/json` header, the same unknown-process request
returns an HTML HTTP 404 page. This demonstrates why the client should ask for
JSON while still being able to handle text or HTML error bodies.
