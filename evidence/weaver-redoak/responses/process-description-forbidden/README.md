# Advertised process description returns HTTP 403

The public process list advertised
`/processes/EchoProcess:1.0.0` as the JSON description of the current process
revision. A direct GET returned HTTP 403 with a generic nginx HTML body.
The unversioned `/processes/EchoProcess` URL returned the same response.

This is not a browser CORS failure. The server returned HTTP 403 to a direct
request. The client should report that the process description could not be
loaded and include the server status or message; it cannot generate a form
without a description.
