# Async preference answered synchronously

Source server: `pygeoapi-demo`

The `hello-world` description advertises both `sync-execute` and
`async-execute`. This request included `Prefer: respond-async`, but the server
returned the completed result with HTTP 200 and `Preference-Applied: wait`.
No job was created.

The client should use the actual response status and headers. An async
preference does not guarantee that the response will contain a job ID or
monitoring URL.
