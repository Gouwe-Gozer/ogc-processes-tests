# Fixed Bearer authentication test gate

This Python gate checks a fixed token before forwarding a request to an existing
API. The API still supplies discovery, processes, jobs and results. The gate
provides no OGC processes of its own.

```text
OAP or curl -> http://localhost:5002 -> backend on http://127.0.0.1:5012
                  checks token           runs the process
```

Use Python 3.11 or later. No Python packages need installing.

```bash
python3 auth/bearer_gate.py
```

The default token is `local-test-token`, deliberately public test data. Change
it with the `OGC_TEST_BEARER_TOKEN` environment variable. This is a local testing
utility, not a production authentication service.

To use another backend or browser origin:

```bash
python3 auth/bearer_gate.py --upstream http://127.0.0.1:5012 \
  --origin http://localhost:5173
```

`--origin` can be repeated. It replaces the default allowed browser origin.
The gate listens on loopback; `--host` and `--port` can change that. The upstream
argument is a fixed HTTP(S) origin, without a path, query or credentials.

## Behaviour

- Every GET, HEAD, POST and DELETE needs the configured Bearer token.
- Missing or wrong credentials return 401 with `WWW-Authenticate` and a JSON
  problem. The request never reaches the backend.
- OPTIONS preflights need no token. Only configured origins, supported methods
  and allowed headers are permitted. CORS headers also accompany failures.
- An accepted request retains its path, query, method, body and relevant headers.
  Authorization and cookies are consumed/dropped, not sent to the backend.
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

These 12 Python tests make real HTTP requests over temporary loopback ports.
Their backend is a small test-only byte responder. They check the gate itself:
credentials, preflight, error handling, forwarding and file bytes. They do not
run OAP, DIRECTED, a browser or OAuth.

The [constructed core tests](../tests/constructed/README.md#access-failures)
separately check OAP's handling of prepared refusals. Neither group proves
successful authentication by the OAP web app. The OAP developers must add
service-specific credential handling before its successful-login checks can
run against this gate.
