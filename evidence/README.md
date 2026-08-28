# Supporting evidence

This folder keeps provider-specific material that may help explain client or
server behaviour but is not part of the small representative set in
[`../scenarios/`](../scenarios/).

The five server folders contain server details and captured material:

- [`zoo-local/`](zoo-local/): 53 runnable requests plus captured process
  descriptions, execution responses, errors, and diagnostics;
- [`pygeoapi-demo/`](pygeoapi-demo/): details of the public pygeoapi demo used
  for the recorded `hello-world` exchanges;
- [`bgt-prototype/`](bgt-prototype/): details of the local pygeoapi-based BGT
  prototype;
- [`directed-local/`](directed-local/): a local pygeoapi process with
  undocumented array constraints and a large CSV result;
- [`weaver-redoak/`](weaver-redoak/): public Weaver discovery responses, a
  missing-CORS observation, and an advertised process description that returned
  HTTP 403.

## How evidence is organized

Evidence is grouped first by server deployment, such as `zoo-local` or
`pygeoapi-demo`. This makes the source of every observation clear. Inside a
server folder, files are grouped by what they are used for:

| Folder | What it contains |
|---|---|
| `requests/` | Requests that can be sent again with the repository scripts |
| `responses/descriptions/` | Process descriptions returned by the server |
| `responses/executions/` | Raw process or job result bodies |
| `responses/catalogs/` | Summaries built from several captured responses |
| `responses/diagnostics/` | Investigation notes and checks that are not normal API responses |
| `exchanges/` | A request and its response stored together, with a README explaining why the observation matters |

This layout is useful for batch work. For example, a script can find all
runnable requests under `requests/` or recapture all process descriptions into
`responses/descriptions/` without walking through every process folder.

The trade-off is that all files for one process are not necessarily beside each
other. To find ZOO material for `Buffer`, search for its process ID:

```bash
rg -l '"process_id": "Buffer"' evidence/zoo-local/requests
```

Its captured description is
[`zoo-local/responses/descriptions/Buffer.process.json`](zoo-local/responses/descriptions/Buffer.process.json).
A layout with one folder per process would make this lookup easier, but would
make the batch operations above less direct. The current layout favours
collecting and comparing many processes.

## Evidence request format

An evidence `request.json` is a small set of instructions for our scripts. It is
not an OGC standard, and the complete file is not sent to the server.

For example:

```json
{
  "id": "hellojs_string",
  "title": "Execute hellojs with a string input",
  "process_id": "hellojs",
  "execution_mode": "sync",
  "method": "POST",
  "path": "/processes/hellojs/execution",
  "headers": {
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "body": {
    "inputs": {
      "S": "Codex"
    }
  },
  "expected_status": 200,
  "notes": "Basic literal-input smoke test."
}
```

Only four parts describe the HTTP request:

| Field | Sent as part of the HTTP request? | Purpose |
|---|---:|---|
| `method` | Yes | HTTP method, such as `GET`, `POST`, or `DELETE` |
| `path` or `url` | Yes | Address to call; the script combines a relative path with the server's base URL |
| `headers` | Yes | HTTP request headers |
| `body` | Yes | JSON body sent by a `POST` request |
| `id` | No | Short repository name shown by the runner and Postman |
| `title` | No | Human-readable explanation of the request |
| `process_id` | No | Process identifier used by the Postman generator to add a description request |
| `execution_mode` | No | Notes whether the example is synchronous or asynchronous |
| `fixture` | No | Points readers to a local input file used by the example |
| `expected_status` | No | Lets the runner report whether the observed status was expected |
| `notes` | No | Extra context for readers and the generated Postman request |

At present, `title`, `execution_mode`, and `fixture` are documentation for
people reading the files; the scripts do not use them. The other metadata
fields have the specific script uses listed above.

`process_id` is related to the real API path, but it is still repository
metadata. For example, `process_id: "Buffer"` corresponds to
`/processes/Buffer/execution`; the server never receives a separate
`process_id` field. Keep these values consistent when editing a request.

Do not pass the whole `request.json` file to `curl --data`. Only the value under
`body` becomes the JSON request body. The method, URL, and headers become their
normal HTTP equivalents.

Files under `exchanges/` use a smaller version of the same request envelope.
Their matching response file records the HTTP `status`, response `headers`,
`final_url`, and response `body`. These are also repository records, not a
standard OGC testcase format.

Names such as `Handling` and `Expected client handling` in exchange notes are
plain-language explanations. They do not define a required client API or a
provider-specific adapter.

Run a ZOO evidence request with
[`../scripts/run_evidence_request.py`](../scripts/run_evidence_request.py).
