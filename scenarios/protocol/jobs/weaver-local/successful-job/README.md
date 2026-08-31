# Successful Weaver asynchronous job

Process: `EchoProcess`
Source server: `weaver-local`

Weaver accepts the request with HTTP 201, reports `accepted` in the submission
body, later reports `successful`, and returns the result document with HTTP
200.

Unlike the selected ZOO submission, Weaver's accepted response has no `links`
array. The protocol core should obtain the monitor URL from the `Location`
header. The polling response then provides the results link.

The Postman scripts save `jobId` and `jobUrl`, repeat polling when a live run
returns `accepted` or `running`, save `resultsUrl` after success, and use it for
the final request. Only the successful polling response was captured; the ZOO
scenario retains the recorded `running` response needed for that state.
