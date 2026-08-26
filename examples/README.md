# Representative exchanges

This folder contains a small set of OGC API Processes HTTP exchanges that are
useful when implementing the client. Each example records what was sent, what
was returned, and why the exchange matters.

These files are fixtures and documentation. They do not run assertions by
themselves. Client tests can load them through the client's normal test
framework.

Placeholders such as `{{baseUrl}}`, `{{jobId}}`, and `{{jobUrl}}` stand for
values supplied by a deployment or obtained from an earlier response.

The initial set contains:

- a successful synchronous execution with inline GeoJSON;
- a complete successful asynchronous job;
- a non-JSON HTTP error returned while polling a job.
