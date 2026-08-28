# Provider evidence

This folder contains requests and responses observed from real OGC API
Processes deployments. Evidence is grouped first by provider and then by API
operation.

```text
evidence/<provider>/
├── server.json
├── captures/
│   ├── discovery/
│   ├── descriptions/
│   ├── executions/
│   └── jobs/
└── diagnostics/
```

The provider folders are:

- [`zoo-local/`](zoo-local/): the local ZOO-Project deployment;
- [`pygeoapi-demo/`](pygeoapi-demo/): the public pygeoapi demo;
- [`bgt-prototype/`](bgt-prototype/): a local pygeoapi-based prototype;
- [`directed-local/`](directed-local/): a local pygeoapi deployment with a
  large CSV result;
- [`weaver-redoak/`](weaver-redoak/): a public Weaver deployment.

## What a capture contains

A normal one-step capture keeps the request and its observed response together:

```text
captures/executions/buffer_polygon/
├── request.json
├── response.json
└── notes.md
```

- `request.json` contains the HTTP method, URL, headers, and request body.
- `response.json` contains the status, headers, final URL, and actual response
  body.
- `notes.md` is optional. It explains why an unusual result may matter.

Multi-step job captures use numbered filenames:

```text
captures/jobs/successful-job/
├── 01-submit.request.json
├── 01-submit.response.json
├── 02-poll.request.json
├── 02-poll.response.json
├── 03-results.request.json
└── 03-results.response.json
```

Errors stay with the operation that returned them. For example, an execution
that returned HTTP 500 remains under `captures/executions/`.

## Complete and incomplete historical captures

The standard format is a matching `request.json` and `response.json` pair.
Some older evidence was not originally stored that way:

- `request.json` without a response means the old response was lost;
- `response-body.json` means the real body survived, but its status, headers,
  and final URL did not;
- `*.response-observation.json` records the size and shape of a large response
  whose full body was not committed.

These are temporary incomplete captures. Rerunning them should add a normal
`response.json`. The incomplete file can then be removed after the new capture
has been checked.

There is no separate folder for missing responses. They can be found from the
absence of a response file in the case folder.

## Request file format

Request files are instructions for the repository scripts. The format is not
part of the OGC standard.

```json
{
  "id": "hellojs_string",
  "title": "Execute hellojs with a string input",
  "process_id": "hellojs",
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
  "expected_status": 200
}
```

Only `method`, `path` or `url`, `headers`, and `body` define the HTTP request.
Fields such as `id`, `title`, `process_id`, `fixtures`, `expected_status`, and
`notes` help people and repository scripts; they are not sent to the provider.

## Response file format

JSON and reasonably sized text bodies are stored directly:

```json
{
  "status": 200,
  "headers": {
    "Content-Type": "application/json"
  },
  "final_url": "http://localhost/ogc-api/processes/Buffer/execution",
  "body": {
    "Result": {
      "value": {
        "type": "FeatureCollection"
      }
    }
  }
}
```

A large or binary body may be stored beside the response. In that case,
`response.json` uses `body_file` instead of `body`.

## Running and completing captures

Print a request as `curl`:

```bash
python3 scripts/run_evidence_request.py hellojs_string --print-curl
```

Send it without changing the repository:

```bash
python3 scripts/run_evidence_request.py hellojs_string
```

Save a complete response beside its request:

```bash
python3 scripts/run_evidence_request.py hellojs_string --save-response
```

An exact request-file path can be used when a case contains several steps.

## Finding result shapes

Because all complete execution responses use the same filenames and envelope,
they can be searched together. For example:

```bash
rg -l 'FeatureCollection' evidence/*/captures/executions
rg -l 'text/csv' evidence/*/captures/executions
rg -l '"href"' evidence/*/captures/executions
```

This allows result bodies to be classified without separating them from the
requests that produced them.
