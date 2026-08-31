# Accepted async job followed by a process-package failure

Weaver accepts the valid `file2string_array` request with HTTP 201. Polling
later reports `failed`, and the results endpoint returns a structured HTTP 400
`JobResultsFailed` response.

The job log identifies the same built-in CWL defect as the synchronous capture:
the command points to a Python executable that is absent from the published
`latest-worker` image.

This sequence is useful to the client because HTTP 201 means accepted, not
successful. The client must poll until a terminal state and then show the
server's failure message.
