# Non-JSON job error

This defensive scenario represents a job endpoint returning HTTP 500 with an
HTML body instead of an OGC JSON problem document. It is not tied to a live
deployment.

A client should keep the status, headers, final URL, content type, and raw body.
It can show a generic error message when no structured problem details are
available. The HTML must not be rendered as trusted application markup.
