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
- [`weaver-local/`](weaver-local/): a local Weaver deployment with complete
  discovery, descriptions, successful sync and async execution, and recorded
  process and output-access failures;
- [`weaver-redoak/`](weaver-redoak/): a public Weaver deployment.

## Provider diagnostics

`diagnostics/` contains provider checks that are useful to the client project
but are not OGC API Processes operations. CORS preflight evidence is stored as:

```text
evidence/<provider>/diagnostics/cors/execution-preflight/
├── request.json
├── response.json
└── notes.md
```

The OPTIONS request represents the check a browser performs automatically
before a cross-origin JSON execution. The notes state whether a browser would
allow the actual POST and why. These requests are not sent by the protocol core
and are not included in the generated Postman evidence collections.

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

## Complete captures

Every stored request should have a complete response. The standard format is a
matching `request.json` and `response.json` pair. A response records:

- the HTTP status;
- the response headers;
- the final URL after redirects;
- the body itself, or `body_file` for a large or binary body stored beside it.

A request may have more than one named response when the same request was
observed in different states. For example, one polling request can have both a
`running` and a `successful` response.

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
