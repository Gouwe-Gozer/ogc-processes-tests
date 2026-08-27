# Representative exchanges

This folder is the small, curated selection of OGC API Processes HTTP
exchanges intended for future client tests. It is a holding area for test
material, not an executable test suite. See the
[repository scope and test strategy](../docs/test-strategy.md) before changing
its structure or adding test machinery.

Each example records what was sent, what was returned, and why the exchange
matters.

Placeholders such as `{{baseUrl}}`, `{{jobId}}`, and `{{jobUrl}}` stand for
values supplied by a deployment or obtained from an earlier response.

The initial set contains:

- a successful synchronous execution with inline GeoJSON;
- a complete successful asynchronous job;
- a non-JSON HTTP error returned while polling a job.
