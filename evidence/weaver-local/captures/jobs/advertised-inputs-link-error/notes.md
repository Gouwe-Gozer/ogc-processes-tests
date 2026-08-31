# Advertised job-inputs link returns HTTP 500

The successful job status advertises an `inputs` link. Following that link with
`Accept: application/json` returned a structured HTTP 500 response.

The core client does not need this optional job-detail endpoint for normal
polling or result retrieval. The capture remains useful evidence that an
advertised link can fail even when the job itself succeeded.
