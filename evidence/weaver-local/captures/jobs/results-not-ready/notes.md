# Results requested before an accepted job is ready

The results request was sent immediately after Weaver accepted the async job.
Weaver returned a structured HTTP 404 `JobResultsNotReady` response. Its body
states that the job was still `accepted` and provides status and monitor links.

This is not a failed job. The client should continue polling instead of showing
the response as a permanent failure.
