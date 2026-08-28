# Successful asynchronous job

This interaction was captured from the ZOO `longProcess` process on 25 August
2026. Job IDs and URLs are represented by placeholders.

The three requests show:

1. submission with `Prefer: respond-async` and HTTP 201;
2. polling, with recorded examples for both a running and a successful job;
3. retrieval of the result document.

HTTP 201 means that the job was accepted, not that processing succeeded. A
client should follow the job URL, stop polling at a terminal state, and fetch
the results only after success.

The generated evidence collection includes these requests without JavaScript
automation. The automated version is the representative
[`successful-job`](../../../../../scenarios/protocol/jobs/zoo-local/successful-job/)
scenario.
