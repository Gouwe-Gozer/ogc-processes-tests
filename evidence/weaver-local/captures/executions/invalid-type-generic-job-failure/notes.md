# Invalid input type produces a generic failed job

The description requires a text value, but this request sends a number. Weaver
starts a job and returns a failed job document with HTTP 400. The job log says
only that the job failed while fetching input definitions; it does not name the
invalid value or expected type.

The client should validate the type from the process description. If this
response is still received, it can show the returned job failure without
claiming that the server identified the bad field.
