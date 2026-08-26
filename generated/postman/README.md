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

The representative collection includes example responses, but it does not
automatically save job IDs or poll jobs. Use it as request documentation and
for manual tests.

Do not edit the generated JSON files. Change an example, evidence request,
server file, or the generator and run the command again.
