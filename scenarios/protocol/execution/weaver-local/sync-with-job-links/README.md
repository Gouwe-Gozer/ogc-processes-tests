# Synchronous result with additional job links

Process: `EchoProcess`
Source server: `weaver-local`

Original evidence:

- [successful synchronous execution](../../../../../evidence/weaver-local/captures/executions/echo-success-sync/)

Weaver returns the requested document result immediately with HTTP 200. It also
records the synchronous execution as a job and includes `Content-Location` and
`Link` headers for status, results, outputs, logs, and provenance.

The protocol core should return the synchronous body immediately. The
additional links may be preserved as response metadata, but they do not turn
the response into an asynchronous submission or start polling.

Form generation and the meaning of the individual inputs are covered by the
separate
[`forms/inputs/weaver-local/mixed-values-map-and-files`](../../../../forms/inputs/weaver-local/mixed-values-map-and-files/)
scenario.
