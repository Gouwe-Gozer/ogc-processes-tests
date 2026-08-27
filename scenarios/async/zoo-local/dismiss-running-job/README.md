# Dismiss a running asynchronous job

Process: `longProcess`
Source server: `zoo-local`

The scenario submits an asynchronous job and sends `DELETE` to the returned job
URL while it is running. ZOO returns a terminal job document with status
`dismissed`.

The protocol core should distinguish dismissal from aborting a local HTTP
request, stop polling, and avoid fetching results. Additional requests made
after dismissal remain in supporting evidence because they do not change the
normal dismissal flow.
