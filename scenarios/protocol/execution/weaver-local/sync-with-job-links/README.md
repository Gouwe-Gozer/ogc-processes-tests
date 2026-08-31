# Synchronous result with additional job links

Process: `EchoProcess`
Source server: `weaver-local`

Weaver returns the requested document result immediately with HTTP 200. It also
records the synchronous execution as a job and includes `Content-Location` and
`Link` headers for status, results, outputs, logs, and provenance.

The protocol core should treat the HTTP 200 body as the synchronous result. It
may preserve the additional links, but it must not mistake this response for an
asynchronous HTTP 201 submission that requires polling.

The rich request and result can later be reused by form and result tests. Their
data complexity is not the main protocol assertion here.
