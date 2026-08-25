# Asynchronous jobs, polling, results, and dismissal

This first client suite covers the asynchronous state machine independently of
the 22 process representatives. Output parsing is exercised once at the final
results step and should use the same result-document parser as synchronous
execution. A cross-product of every process input/output family with every job
state is unnecessary.

The request sequence follows OGC API - Processes Part 1: Core:

```text
POST process execution with Prefer: respond-async
  └─ 201 + Location: job accepted, not completed
       ├─ GET job: accepted/running → may be polled again
       ├─ GET job: successful → follow the results link
       ├─ GET job: failed → expose the terminal message
       └─ DELETE job: dismissed when that capability is advertised
```

See the official
[OGC API - Processes Part 1: Core](https://docs.ogc.org/is/18-062r2/18-062r2.html)
for the core job resources and optional Dismiss requirements class.

## Coverage priority and error-message policy

The baseline tier is the minimum client acceptance suite. It verifies the job
state machine, description-driven validation, structured problems, safe error
fallback, and shared result parsing.

The robustness tier contains deterministic parser fixtures for malformed or
incomplete responses. They are valuable implementation tests, but they do not
require custom UI treatment and are not separate tender-critical behaviours.
Keeping them is inexpensive because they run through a mock transport rather
than creating live jobs.

For both tiers, useful server messages can normally be displayed safely and
largely unchanged:

```text
Job failed — server message: “<server message>”
```

The client does not need a translation catalogue for individual ZOO, GDAL,
SAGA, or OTB messages. It must still escape returned text, retain the raw body,
provide a generic fallback for missing or non-JSON detail, and correctly
classify HTTP success, HTTP problems, and job terminality independently of the
message wording.

## Initial coverage

| Tier | Category | Scenario | Main client behaviour |
|---|---|---|---|
| Baseline | Live lifecycle | `successful-long-process` | Submit, poll running, stop at successful, fetch and parse results |
| Baseline | Live lifecycle | `failed-demo-process` | Accepted submission later becomes failed; safely display the server message |
| Baseline | Live lifecycle | `dismiss-running-job` | DELETE is distinct from aborting a browser request; handle the dismissed document and later missing resource |
| Baseline | Request error | `description-invalid-input` | Catch a wrong primitive type before ordinary submission; do not trust server acceptance as schema validation |
| Baseline | Request error | `results-not-ready` | Preserve the `ResultNotReady` problem and continue treating the job as non-terminal |
| Baseline | Request error | `unknown-job` | Preserve `NoSuchJob`; do not recreate or silently forget the job |
| Baseline | Response handling | `non-json-job-error` | Provide a safe generic error while retaining status and raw body |
| Robustness | Response handling | `accepted-with-body-monitor-link` | Resolve a body monitor link if the required Location header is absent |
| Robustness | Response handling | `accepted-without-job-location` | Report that an accepted job cannot be monitored |
| Robustness | Response handling | `malformed-job-status` | Return a parse/protocol error with status and raw body |
| Robustness | Response handling | `unknown-job-status` | Preserve an extension state without guessing terminality |
| Robustness | Response handling | `successful-without-results-link` | Keep job success distinct from failure to discover its result resource |
| Robustness | Response handling | `malformed-results-link` | Preserve job success but do not fetch an invalid results URL |

The live response fixtures were captured from and normalized for profile
`zoo-ubuntu18-gdal3-saga7-otb7` on 2026-08-25. In this profile:

- async submission returns `201`, `Preference-Applied: respond-async`, a
  `Location` header, and a status body that can already say `running`;
- a running `longProcess` exposes integer progress and a message;
- premature results return HTTP 404 with a `ResultNotReady` problem;
- successful dismissal returns HTTP 200 with status `dismissed`;
- a subsequent GET or repeated DELETE returns HTTP 404 `NoSuchJob` rather than
  the HTTP 410 described for repeated dismissal by the standard.

That final difference is profile evidence, not a new client rule. The client
must preserve the actual HTTP problem and should not hard-code ZOO's deviation
as universal behaviour.

## Polling rules tested here

- A `201` submission means accepted, never process success.
- Use the case-insensitive `Location` response header as the primary job URL.
  A usable monitor link in the response body is a fallback. Resolve relative
  links against the final response URL.
- Treat `accepted` and `running` as non-terminal; treat `successful`, `failed`,
  and `dismissed` as terminal.
- Preserve progress, messages, timestamps, links, and unknown fields. Do not
  require optional progress or message fields to exist.
- Fetch results only after `successful`, using the advertised OGC results link.
- A failed job does not have successful results merely because submission was
  accepted.
- Aborting a local GET with `AbortSignal` only stops that HTTP request. It does
  not dismiss the server job. Dismissal requires the explicit DELETE request.
- Do not automatically re-POST a process after a polling, parsing, or network
  error. POST is not idempotent and could create duplicate work.

## Deliberate exclusions for now

- `GET /jobs` belongs to the optional Job List requirements class and is not
  needed for the promised per-job lifecycle.
- callbacks, automatic retry/backoff, persistent background polling, and job
  history are outside the current tender core.
- transport abort behaviour needs a small code-level mock test; it is not a
  distinct server API request fixture.
- referenced raster results can later add one async integration scenario if a
  tested service exposes a stable long-running process for it. The result-link
  and result-document handling itself is already represented here.
