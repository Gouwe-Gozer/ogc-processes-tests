# Fixed Bearer-token and API-key test gate

This Python gate checks a fixed Bearer token or API key before forwarding to
an existing API. The API still supplies discovery, processes, jobs and results.
The gate provides no OGC processes of its own.

```text
OAP or curl -> http://localhost:5002 -> backend on http://127.0.0.1:5012
                  checks credential      runs the process
```

Use Python 3.11 or later. No Python packages need installing.

```bash
python3 auth/bearer_gate.py
```

Bearer is the default mode; its token is `local-test-token`. Change it with
`OGC_TEST_BEARER_TOKEN`. API-key mode uses `local-test-api-key`, configurable
with `OGC_TEST_API_KEY`. Both defaults are deliberately public test data.
This is a local testing utility, not a production authentication service.
The filename remains `bearer_gate.py`; it now supports both modes.

To use another backend or browser origin:

```bash
python3 auth/bearer_gate.py --upstream http://127.0.0.1:5012 \
  --origin http://localhost:5173
```

`--origin` can be repeated. It replaces the default allowed browser origin.
The gate listens on loopback; `--host` and `--port` can change that. The upstream
argument is a fixed HTTP(S) origin, without a path, query or credentials.

## Start with DIRECTED

The expected layout is the same parent folder for this repository and the
[DIRECTED fork](https://github.com/Gouwe-Gozer/pygeoapi_processes):

```text
parent-folder/
├── ogc-processes-tests/
└── pygeoapi_processes/
```

From `ogc-processes-tests`, start a separate backend:

```bash
docker compose -f auth/compose.yml up -d --build
```

This builds the fork's existing Dockerfile using its source and included
Denmark data. It reads that checkout without changing its files. The first
build can take a while. It creates its own Compose project and image, separate
from an existing DIRECTED deployment on port 5000.

The backend is published on loopback port **5012**. Our
[config](directed-config.yml) sets `server.url` to **http://localhost:5002**, so
advertised process, execution, status and results addresses lead through the
gate. pygeoapi's [configuration documentation](https://docs.pygeoapi.io/en/stable/configuration.html)
describes `server.url`; this is separate from the port on which Docker publishes
the backend. Response payloads are not rewritten by the gate.

Keep the gate running in a second terminal:

```bash
python3 auth/bearer_gate.py
```

Clients should connect to **http://localhost:5002**. Check it from another
terminal, starting with small discovery requests:

```bash
# No token: 401 from the gate, even if the backend is stopped.
curl -i http://localhost:5002/processes

# Wrong token: 401 from the gate.
curl -i -H 'Authorization: Bearer wrong' http://localhost:5002/processes

# Correct token: the real DIRECTED process list.
curl -i -H 'Authorization: Bearer local-test-token' \
  -H 'Accept: application/json' \
  http://localhost:5002/processes

# Correct token: the real CLIMADA process description.
curl -i -H 'Authorization: Bearer local-test-token' \
  -H 'Accept: application/json' \
  http://localhost:5002/processes/climada-simple-example-denmark-process
```

Inspect the returned links: API links should point at port 5002. If they point
at 5000 or 5012, fix the backend's public URL before testing a complete workflow.
A correct token followed by 502 means the gate could not read the backend; check
`docker compose -f auth/compose.yml logs directed`.

To execute the actual Denmark calculation and save its response:

```bash
curl -sS -D - -o directed-auth-result.csv \
  -H 'Authorization: Bearer local-test-token' \
  -H 'Content-Type: application/json' \
  --data '{"inputs":{"intensity":[0,30,80]}}' \
  http://localhost:5002/processes/climada-simple-example-denmark-process/execution
```

This runs the real calculation. Our earlier unprotected capture returned a
large CSV; inspect the status and Content-Type before interpreting the saved
body. An error body may also be written to that filename. The gate's 300-second
socket timeout can be raised for slower calculations. An interrupted or timed-out
POST may have reached the backend; the gate will not repeat it automatically.

Stop the gate with Ctrl+C, and stop the separate backend with:

```bash
docker compose -f auth/compose.yml down
```

To use another machine or port, change `server.url` in `auth/directed-config.yml`
to the gate's client-visible address, recreate the backend, and set the gate's
`--host`, `--port` and allowed `--origin` accordingly. Token authentication uses
HTTP here only for the local test setup; use HTTPS when sending real credentials.

## API-key mode

Use the same DIRECTED backend and ports described above. Stop the running gate
with Ctrl+C, then start it in API-key mode instead:

```bash
python3 auth/bearer_gate.py --auth api-key
```

The default header is `X-API-Key`, and the default key is `local-test-api-key`.
From another terminal:

```bash
# Missing key: 403.
curl -i http://localhost:5002/processes

# Wrong key: 403.
curl -i -H 'X-API-Key: wrong' http://localhost:5002/processes

# Correct key: the real DIRECTED process list.
curl -i -H 'X-API-Key: local-test-api-key' \
  -H 'Accept: application/json' http://localhost:5002/processes
```

To run the Denmark calculation and save the returned body:

```bash
curl -sS -D - -o directed-auth-result.csv \
  -H 'X-API-Key: local-test-api-key' \
  -H 'Content-Type: application/json' \
  --data '{"inputs":{"intensity":[0,30,80]}}' \
  http://localhost:5002/processes/climada-simple-example-denmark-process/execution
```

Check the status and Content-Type before treating the file as CSV. The same
key header is required on subsequent job-status and result requests too.

The header name is configurable. For example, to match the constructed client
acceptance cases, restart the gate with:

```bash
python3 auth/bearer_gate.py --auth api-key --api-key-header X-Processing-Key
```

Then send `X-Processing-Key: local-test-api-key` instead of `X-API-Key`.
The selected header is also allowed in browser preflights from configured
origins. Header names are case insensitive; key values are matched exactly.
This gate accepts nonempty visible ASCII keys without spaces. Choose a custom
header name, not `Authorization`, `Host`, framing headers or browser-control
headers. Invalid configuration fails at startup without printing the key.

Only the selected credential mode grants access. A Bearer token does not
replace an API key. Missing, wrong or duplicate keys return 403 with a JSON
problem and no Bearer challenge; 403 is this example's choice, not a universal
rule for API-key services. The key is checked and consumed by the gate, so it
is never forwarded to DIRECTED. There is no key in a URL or cookie.

## Handoff to OAP developers

Start with direct browser access to port 5002. Implement credential handling in
OAP and exercise that implementation against this gate:

1. Let the user set a Bearer token or a key plus its header name for this
   service, initially held in memory.
2. Attach it through OAP's existing injectable fetch on discovery, page reads,
   description, execution, polling, dismissal and result requests. Also cover
   downloads made separately by the web app.
3. Scope it to the configured service. Links and redirects to other destinations
   must not automatically receive the token.
4. Check missing, wrong and correct tokens. With the correct token, follow the
   real service's links through a full calculation; with a refusal, retain its
   explanation and avoid resubmitting the calculation.

The current OAP npm package has no credential UI. These curl commands prove the
gate and backend interaction, not OAP's implementation. The Python gate tests
also do not validate client-side token scoping to other hosts.

Relay support is a separate implementation step: its session token belongs to
the browser-to-relay connection. A service token would need to be configured
and attached on the relay-to-service connection, with appropriate challenge
headers passed back. Our gate expects the service token.

The two modes are fixed Bearer tokens and API keys in a configurable header.
Basic Auth, OAuth login/refresh, users, roles and token expiry are not implemented.

## Behaviour

- Every GET, HEAD, POST and DELETE needs the selected credential.
- Missing, wrong or duplicate credentials return a JSON problem: 401 with
  `WWW-Authenticate` in Bearer mode, or 403 in API-key mode. The request never
  reaches the backend.
- OPTIONS preflights need no token. Only configured origins, supported methods
  and allowed headers are permitted. CORS headers also accompany failures.
- An accepted request retains its path, query, method, body and relevant headers.
  The selected key header, Authorization and cookies are not sent to the backend.
- Replies retain their status, body and relevant headers, including `Location`,
  `Link` and `WWW-Authenticate`. Bodies stream in chunks, including large files.
  There is no payload rewriting, redirect following or automatic request retry.
- The gate owns CORS headers and does not relay cookies. Browser code can read
  the returned challenge, job/result links and file metadata.
- Request bodies require Content-Length and are limited to 16 MiB. The socket
  timeout defaults to 300 seconds and can be changed with `--timeout`.

The backend must advertise this gate's address in its links. A backend link
pointing directly at its unprotected port would bypass the test. The gate
passes such links unchanged so that configuration mistakes remain visible.

## What is tested

```bash
python3 -m unittest discover -s auth -p 'test_*.py' -v
```

These 32 Python tests exercise both modes over temporary loopback HTTP ports
and reject invalid configuration before the gate starts.
Their backend is a small test-only byte responder. They check the gate itself:
credentials, preflight, error handling, forwarding and file bytes. They do not
run OAP, DIRECTED, a browser or OAuth. A separate
[GitHub Actions job](../.github/workflows/auth-gate.yml) runs these same checks
without Docker or a sibling checkout. They are separate from the Node suite
run by `npm run check`. That suite now includes [auth acceptance cases](../tests/acceptance/)
for explicit Bearer and API-key headers and client reactions to protected
discovery, execution, polling and results. All ten auth checks run normally;
failures are visible alongside the other client tests. They use the existing
fake transport to enforce the service's credential requirement, not this Python
gate. No test helper supplies credentials for OAP. The gate's Python tests
never contribute to npm client test counts.

The [constructed core tests](../tests/constructed/README.md#access-failures)
separately check OAP's handling of prepared refusals. Neither group proves
successful authentication by the OAP web app. The OAP developers must add
service-specific credential handling before its successful-login checks can
run against this gate.

### Live DIRECTED check — 1 October 2026

The profile also passed a live check using the already-built
`pygeoapi_processes-pygeoapi` image, which reports pygeoapi `0.25.dev0`.
Its image ID was
`sha256:f1e748b3eb960c2c3142f076f669dfdb761f7fa57ef81eec656827ced01ee2ce`.
The original service on port 5000 stayed running. A separate container used
this profile on port 5012, with the gate on port 5002.

| Request | Observed result |
| --- | --- |
| Process list with missing or wrong token | 401 with a Bearer challenge and CORS headers |
| Landing page, process list and CLIMADA description with correct token | 200; local API links used port 5002 |
| Execution preflight from `http://localhost:5173`, allowing `authorization,content-type,prefer` | 204 without a token |
| Submission with `{"inputs":{"intensity":[0,30,80]}}` and `Prefer: respond-async` | 201; `Location` used port 5002 |
| Following that job with the correct token | Accepted, then successful |
| Following its result link with the correct token | 200, `text/csv`, 18,849,968 bytes |
| Submission, job status and result requests with missing or wrong token | 401 |

The CSV was byte-for-byte identical to the same job's result fetched directly
from the backend. Its SHA-256 was
`676ec1ac1862942992367c8eb7ab5de7328ae92047777375e427fdacc9cd06d6`.
The 12 automated Python gate tests also passed.

To reuse that existing local image instead of building, the check started the
backend with this override, followed by `python3 auth/bearer_gate.py`:

```bash
docker compose -f auth/compose.yml -f - up -d --no-build --pull never <<'YAML'
services:
  directed:
    image: pygeoapi_processes-pygeoapi
YAML
```

This check used Python HTTP requests. It verified the returned CORS headers,
but did not run a browser or OAP's authentication implementation. Building a
fresh image was not part of this check. The temporary gate and backend were
stopped afterwards; the original service was left running.

#### API-key follow-up — 1 October 2026

The same image and separate DIRECTED profile were checked with both the default
`X-API-Key` header and custom `X-Processing-Key`. Missing/wrong keys returned
403, the correct key returned the real process list, and each header passed
its unauthenticated execution preflight. A Bearer token alone was refused.

With `X-Processing-Key`, one real asynchronous calculation returned 201 with
a gate-facing job URL, progressed from accepted to successful, and returned
an 18,849,968-byte CSV with the same SHA-256 shown above. Its bytes matched the
same job's direct backend result. Missing/wrong keys were also refused on the
job-status and result requests. All 32 Python tests passed.

These checks used Python HTTP requests, not OAP or a browser. The temporary
gates and backend were stopped afterwards; the original service on port 5000
stayed running.
