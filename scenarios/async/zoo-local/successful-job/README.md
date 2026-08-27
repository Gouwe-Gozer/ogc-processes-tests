# Successful asynchronous job

This scenario was captured from the ZOO `longProcess` process on 25 August
2026. Job IDs and URLs are represented by placeholders.

The three requests show:

1. submission with `Prefer: respond-async` and HTTP 201;
2. polling, with recorded examples for both a running and a successful job;
3. retrieval of the result document.

HTTP 201 means that the job was accepted, not that processing succeeded. A
client should follow the job URL, stop polling at a terminal state, and fetch
the results only after success.

The `.post-response.js` files are copied into the generated Postman collection.
During a collection run, they save `jobId` and `jobUrl`, repeat the polling
request until the job finishes, and save `resultsUrl` for the final request.
