# Successful asynchronous job

This example was captured from the ZOO `longProcess` process on 25 August
2026. Job IDs and URLs are represented by placeholders.

The four exchanges show:

1. submission with `Prefer: respond-async` and HTTP 201;
2. a running job;
3. a successful job with a results link;
4. retrieval of the result document.

HTTP 201 means that the job was accepted, not that processing succeeded. A
client should follow the job URL, stop polling at a terminal state, and fetch
the results only after success.
