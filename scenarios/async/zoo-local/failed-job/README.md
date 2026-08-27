# Accepted asynchronous submission reaches a failed terminal state

Process: `demo`
Source server: `zoo-local`

The execution request is accepted with HTTP 201. A later status response uses
HTTP 200 but reports the terminal job state `failed`.

The protocol core should not report success from HTTP 201 or from the polling
request's HTTP 200. It should stop polling, retain the status document, and
return the server's job message without fetching results or resubmitting the
process.
