# Postman collections

Generate both collections with:

```bash
python3 scripts/generate_postman_collections.py
```

The command creates:

- `representative-scenarios.postman_collection.json`: the small scenario set,
  including its recorded responses;
- `evidence-requests.postman_collection.json`: all runnable provider-specific
  requests and one process-description request per represented process.

Both collections give each server its own Postman variable, such as
`{{zooLocalBaseUrl}}`, `{{pygeoapiDemoBaseUrl}}`, or
`{{weaverRedoakBaseUrl}}`. The generator selects the variable from the provider
folder, so requests from different services can live in the same collection.
Job steps also use variables such as `{{jobUrl}}` and `{{resultsUrl}}`.

The representative collection includes recorded response examples. Async
submission scripts save `jobId` and `jobUrl` for subsequent status or dismiss
requests. The successful-job workflow also:

1. repeats the status request while the job is `accepted` or `running`;
2. saves `resultsUrl` after a successful status response;
3. lets the next request retrieve the results.

Run the `protocol/jobs/zoo-local/successful-job` folder with the Collection
Runner, Postman CLI, or Newman to use the complete sequence. Sending one
request manually still saves variables, but Postman only follows
`setNextRequest` while running a collection. Change `pollDelayMs` or
`maxPollAttempts` in the collection variables if needed.

Post-response scripts come from matching `.post-response.js` files beside the
scenario requests.

These scripts automate live API inspection in Postman. They are not the future
client implementation or its automated test suite.

Do not edit the generated JSON files. Change a scenario, evidence request,
server file, or the generator and run the command again.
