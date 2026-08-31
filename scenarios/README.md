# Representative scenarios

This folder contains a small, curated selection of OGC API Processes HTTP
scenarios intended for future client tests. It is not an executable test suite.
See the
[repository scope and test strategy](../docs/test-strategy.md) before changing
its structure or adding test machinery.

Scenarios are grouped first by the part of the client they are mainly intended
to test:

```text
scenarios/
├── protocol/
│   ├── discovery/<provider>/<scenario>/
│   ├── execution/<provider>/<scenario>/
│   ├── jobs/<provider>/<scenario>/
│   └── errors/<provider>/<scenario>/
├── forms/
│   ├── inputs/<provider>/<scenario>/
│   └── validation/<provider>/<scenario>/
└── results/
    ├── maps/<provider>/<scenario>/
    ├── tables/<provider>/<scenario>/
    ├── values/<provider>/<scenario>/
    └── downloads/<provider>/<scenario>/
```

The provider level says which API produced the exchange. For example, Weaver,
pygeoapi, and ZOO can all appear below the same behaviour when they provide
useful variations. It does not mean the client should contain provider-specific
code. The provider folder name must match an `evidence/<provider>/server.json`
file; that file supplies the default URL used in the generated Postman
collection.

Each scenario has one primary location, even when it can support more than one
test. For example, the GeoJSON result scenario can also help test synchronous
execution. Tests may reuse a scenario from another section; do not copy the
files into two folders.

## Where synchronous and asynchronous execution fit

The protocol section contains the execution-mode distinction:

- `protocol/execution/zoo-local/simple-sync` is the smallest immediate HTTP 200
  execution;
- `protocol/execution/pygeoapi-demo/raw-versus-document-response` covers two
  more synchronous response modes;
- `protocol/jobs/` covers asynchronous submission, polling, results, failure,
  and dismissal.

Forms and results are not divided into `sync` and `async`. A form is built from
the process input description, and it normally produces the same `inputs`
payload for either execution mode. Result handling is based on the returned
value, reference, and media type, regardless of whether the result arrived in
the execution response or from a completed job.

The protocol core still handles the differences: asynchronous execution adds
job submission and polling, while raw responses, document responses, and job
results can use different envelopes. These protocol details should not require
separate sync and async copies of the same form or result scenario.

There is no `transport/` section here. Transport tests need controlled cases
such as a rejected `fetch`, an aborted request, a redirect, and differently
capitalized headers. Those should be small unit tests beside the future
client's HTTP code. The scenarios in this repository record exchanges with
real API services and mainly support protocol, form, result, and live tests.

The stored records use `{{baseUrl}}` so they remain independent of a test
runner. The Postman generator replaces it with the variable for the provider
folder, such as `{{zooLocalBaseUrl}}` or `{{pygeoapiDemoBaseUrl}}`.
Placeholders such as `{{jobId}}` and `{{jobUrl}}` are obtained from an earlier
response.

Request and response files use matching names:

```text
01-execute.request.json
01-execute.response.json
```

A request can have several recorded response variants, such as
`02-poll.running.response.json` and `02-poll.successful.response.json`.

The current scenarios and the reason each was selected are listed in the
[test strategy](../docs/test-strategy.md#current-representative-scenarios).
The form-specific structure, input encodings, selection, and remaining gaps
are documented in [`forms/README.md`](forms/README.md).
The result wrappers, semantic output types, presentation choices, and
remaining gaps are documented in [`results/README.md`](results/README.md).
