# Results requested before the job is ready

Process: `file2string_array`
Source server: `weaver-local`

The submission is accepted with HTTP 201. An immediate results request returns
HTTP 404 with `title: JobResultsNotReady` and `cause.status: accepted`.

The protocol core should distinguish this temporary response from an unknown
job. It should keep the job available for polling and should not report the
execution as permanently failed.

The later process-package failure is unrelated to this scenario. This scenario
ends with the observed not-ready response.
