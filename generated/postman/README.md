# Postman collections

Generate both collections with:

```bash
python3 scripts/generate_postman_collections.py
```

The command creates:

- `representative-examples.postman_collection.json`: the small example set,
  including its recorded responses;
- `evidence-requests.postman_collection.json`: all runnable provider-specific
  requests and one process-description request per represented process.

Each server has its own Postman variable, such as `{{zooLocalBaseUrl}}`. Job
steps also use variables such as `{{jobUrl}}` and `{{resultsUrl}}`.

The representative collection includes recorded response examples. Its async
workflow also includes post-response scripts that:

1. save `jobId` and `jobUrl` after job submission;
2. repeat the status request while the job is `accepted` or `running`;
3. save `resultsUrl` after a successful status response;
4. let the next request retrieve the results.

Run the `async/successful-job` folder with the Collection Runner, Postman CLI,
or Newman to use the complete sequence. Sending one request manually still
saves variables, but Postman only follows `setNextRequest` while running a
collection. Change `pollDelayMs` or `maxPollAttempts` in the collection
variables if needed.

Post-response scripts come from matching `.post-response.js` files beside the
example requests.

These scripts automate live API inspection in Postman. They are not the future
client implementation or its automated test suite.

Do not edit the generated JSON files. Change an example, evidence request,
server file, or the generator and run the command again.
