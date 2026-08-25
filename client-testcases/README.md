# Client protocol testcases

This directory is the client-facing protocol suite. It contains ordered HTTP
requests, representative transport responses, assertions, and the preferred
client behaviour for both successful and faulty exchanges.

The name `client-testcases` is deliberate:

- [`../cases/`](../cases/) verifies that particular process requests execute
  against the selected ZOO profile;
- [`../evidence/`](../evidence/) preserves observations from that profile;
- `client-testcases/` verifies how the future client handles API exchanges.

The client suite may therefore contain synthetic responses that no healthy
server should produce. Those fixtures are needed to prove that malformed or
incomplete responses result in useful errors instead of crashes or misleading
success messages.

## Layout

```text
client-testcases/
├── README.md
├── async-jobs/
│   ├── live-lifecycle/
│   ├── request-errors/
│   └── response-handling/
├── process-execution/
│   ├── usable-results/
│   ├── server-file-paths/
│   ├── incomplete-results/
│   ├── provider-problems/
│   ├── description-problems/
│   └── validation-errors/
└── implementation-samples/
    └── pygeoapi/
```

- `live-lifecycle` contains complete sequences that can be exercised against
  the current ZOO profile.
- `request-errors` contains description-invalid input or requests made in an
  invalid resource state. Some are manual-only because they deliberately
  create work on the server.
- `response-handling` contains recorded-only transport responses for client
  parser and state-machine tests.
- `process-execution` contains the compact 22-process selection, grouped by
  the handling required from the client instead of provider library.
- `implementation-samples` contains small recorded interoperability fixtures
  from deployments other than the selected ZOO profile. These are neither
  conformance suites nor claims that process-specific behaviour is an
  implementation default.

The compact process suite from
[`../PROCESS_BEHAVIOUR_FAMILIES.md`](../PROCESS_BEHAVIOUR_FAMILIES.md) is
indexed in
[`process-execution/suite.json`](process-execution/suite.json). Its two async
representatives point to the lifecycle fixtures rather than duplicating them.

## File conventions

Every scenario has a `testcase.json`. Its ordered `steps` point to request and
representative-response descriptors.

All referenced paths are relative to the file that contains them. This keeps a
scenario self-contained and makes it safe to move or generate independently.

A `*.request.json` descriptor contains:

- `method`: `GET`, `POST`, or `DELETE`;
- `url`: a URL template;
- `headers`: exact relevant request headers;
- `body_file`: optional path to the raw request body.

A `*.response.json` descriptor models the minimal transport return value:

- `status`;
- `headers`;
- `final_url` after redirects;
- `body_file` containing the raw response bytes used by the protocol test.

JSON response bodies remain separate files so a mock transport can return
their exact bytes. HTML and other non-JSON bodies use the appropriate file
extension. Header names must be interpreted case-insensitively.

Templates currently use:

| Variable | Meaning |
|---|---|
| `{{baseUrl}}` | OGC API base URL without a trailing slash |
| `{{pygeoapiDemoBaseUrl}}` | Official stable pygeoapi demo root |
| `{{bgtPrototypeBaseUrl}}` | Optional local BGT prototype root |
| `{{jobId}}` | Job identifier captured from a response |
| `{{jobUrl}}` | Resolved job monitor URL |
| `{{resultsUrl}}` | Resolved results URL |
| `{{resultUrl}}` | Referenced process-output URL captured from a result wrapper |

Dynamic identifiers and timestamps in representative bodies are normalized.
This makes the fixtures deterministic while retaining the shape observed from
the service.

## Interpreting preferred client behaviour

Each step has an `expected_client_behavior` object:

- `classification` is the protocol outcome exposed by the core;
- `must` lists required behaviour;
- `must_not` lists misleading or unsafe behaviour the test guards against.

Detailed response fixtures do not imply bespoke UI copy for every provider
message. The normal policy is to classify the protocol outcome and safely pass
through useful server text, for example:

```text
Job failed — server message: “Error executing the service”
```

The async suite distinguishes baseline acceptance coverage from additional
robustness fixtures. See [`async-jobs/README.md`](async-jobs/README.md).

These expectations apply to the protocol core. Polling widgets, progress
presentation, form generation, and result rendering remain consumer concerns.
The core may offer a small poll-until-terminal convenience operation, but this
suite does not imply background scheduling, persistence, retries, or request
history.

## Live and recorded use

`live-capable` scenarios contain executable request sequences. Their checked-in
responses are representative assertions, not values to compare byte-for-byte:
job IDs, timestamps, progress, messages, and absolute hosts can vary.

`manual-only` scenarios are executable but either timing-sensitive or expected
to be blocked by normal client preflight. Run every cleanup step when their POST
is deliberately sent.

`recorded-only` scenarios feed the checked-in response through a mock
transport. They are intentionally deterministic and do not require a server
capable of producing a broken response on demand.
