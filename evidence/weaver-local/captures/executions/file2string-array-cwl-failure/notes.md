# Valid input reaches a broken built-in CWL command

The request satisfies the `file2string_array` description. Weaver returned a
failed job document with HTTP 400 for the synchronous execution.

The job log shows the actual process defect: the packaged CWL tries to run
`/usr/local/lib/python3.13/site-packages/bin/python`, which does not exist in
the published `latest-worker` image.

This is not an end-user input error. A client can report the failed job and the
server message, but it should not invent a more specific diagnosis.
