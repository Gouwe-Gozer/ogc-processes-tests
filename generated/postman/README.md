# Postman collections

Generate both collections with:

```bash
python3 scripts/generate_postman_collections.py
```

The command creates:

- `deployment-probes.postman_collection.json`: all runnable probes, grouped by
  server and request type;
- `client-scenarios.postman_collection.json`: the requests and example
  responses from all `live-capable` client testcases.

Each server has its own Postman variable, such as `{{zooLocalBaseUrl}}`. Job
steps also use variables such as `{{jobUrl}}` and `{{resultsUrl}}`.

The client-scenarios collection includes example responses, but it does not
automatically save job IDs or poll jobs. Use it as request documentation and
for manual tests.

Do not edit the generated JSON files. Change the probe, testcase, deployment
file, or generator and run the command again.
