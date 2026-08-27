# Representative scenarios

This folder contains a small, curated selection of OGC API Processes HTTP
scenarios intended for future client tests. It is not an executable test suite.
See the
[repository scope and test strategy](../docs/test-strategy.md) before changing
its structure or adding test machinery.

Scenarios are grouped by API behaviour, then provider, then scenario name.
Each scenario records what was sent, what was returned, and why the exchange
matters.

The provider folder records the source deployment. Use `synthetic` for a
deliberately constructed response that was not captured from a live provider.
It does not imply provider-specific client code.

Placeholders such as `{{baseUrl}}`, `{{jobId}}`, and `{{jobUrl}}` stand for
values supplied by a deployment or obtained from an earlier response.

The current set contains:

- a successful synchronous execution with inline GeoJSON;
- a complete successful asynchronous job;
- a non-JSON HTTP error returned while polling a job.
