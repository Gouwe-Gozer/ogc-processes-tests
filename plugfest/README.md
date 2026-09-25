# Plugfest: getting started

Use this folder to test both visiting clients and visiting OGC API Processes
servers. It is a manual walkthrough using our existing evidence, not a new
automated test framework or a compliance certification.

Start with this guide, follow the [six checks](checklist.md), and copy the
[results template](results-template.md) for each client/server combination.
Keep input and output examples: they help improve forms and result presentation
as well as diagnose protocol problems.

## Two routes

| Route | Use | What it establishes |
|---|---|---|
| Another company's client → known service | The visiting UI and our selected requests as examples | What that client can discover, submit, monitor and display on that deployment |
| Our client → another company's service | The OAP web application and the visiting server's current descriptions | Whether our client works with that server's actual processes and payloads |

A third useful comparison is sending the same request directly with Postman.
It helps distinguish a provider response from client behaviour. Postman success
does not establish browser access: CORS can prevent a web client from sending
a request, reading a reply or seeing headers such as `Location`.

## Prepare before the event

- Obtain working client application URLs or launch instructions from their
  owners, including our OAP web application. This repository does not launch a UI.
- Confirm the service addresses, access requirements and available processes.
  Verify them from a colleague's event machine, including referenced input files.
- Agree which process is a small example, which supports background jobs, and
  which supplies interesting inputs and results. Start with the small example.
- Import the Postman collection below and try the selected requests before the
  session. Keep the repository available locally for the example bodies/files.
- Choose a place to save observations using the results template. Record
  versions and exact addresses so another colleague can reproduce the session.

Fill in this table with event information. **No endpoint is confirmed by this
guide.** The `*-local` defaults in our evidence refer to services on the original
capture machine; cloning this repository does not start or deploy them.

| Service/deployment | Event base URL | Access instructions (no passwords) | Confirmed process IDs | Checked by/date |
|---|---|---|---|---|
| ZOO | To confirm | | | |
| Weaver | To confirm | | | |
| DIRECTED | To confirm | | | |
| Visiting service: … | To confirm | | | |

For each browser client, record its page URL too. Different ports count as
different origins. Record whether a proxy/relay is used; do not silently change
the connection route halfway through a comparison.

## Use the existing Postman collection

Import [representative-scenarios.postman_collection.json](../generated/postman/representative-scenarios.postman_collection.json)
into Postman. It is already generated; no Node installation is required to
read the examples or use the manual checklist. The collection follows the
`scenarios/` folder structure.

In your imported copy, set the applicable collection variables to the confirmed
event addresses, without trailing slashes:

| Provider | Collection variable |
|---|---|
| ZOO | `zooLocalBaseUrl` |
| Local Weaver | `weaverLocalBaseUrl` |
| DIRECTED | `directedLocalBaseUrl` |
| Public pygeoapi example | `pygeoapiDemoBaseUrl` |

Check for environment variables overriding those values. Recorded absolute
URLs, linked files, output links and process IDs are not automatically made
portable by changing a base URL. Inspect them before sending a request.

Run individual requests first. For the known ZOO or Weaver successful-job
scenario, run that specific folder in Collection Runner: its scripts save the
new job address/ID and follow the polling sequence. Reset job variables between
runs; never reuse the IDs from a recorded example. The scripts have a polling
limit; reaching it does not prove the server job failed.

Do not run the entire collection blindly: it mixes deployments, deliberately
failing requests and different processing workloads. The per-provider
[evidence collections](../generated/postman/README.md#provider-evidence) are
additional manual references; they do not include the job automation scripts.

Saved Postman response examples are historical evidence, not freshly obtained
results. Large/binary `body_file` contents remain in this repository and are
not embedded in Postman. To update generated collections after changing source
captures, run `python3 scripts/generate_postman_collections.py`; do not edit the
tracked generated JSON by hand.

## Route A: visiting client, known service

1. Record the visiting client name/version, browser/page URL and service address.
2. Connect through the visiting client's normal UI and read the current process
   description. Confirm that the selected process and inputs actually exist.
3. Follow the checklist. Use its linked request bodies as example values. Let
   the visiting client construct its own request; don't silently replace it
   with a Postman request and call that a client success.
4. When a result is unexpected, compare the actual outgoing request and server
   reply with a direct Postman request. Save differences rather than guessing
   whether the client or server is at fault.
5. Record UI observations: usable controls, preserved values, readable errors,
   useful result display and accessible download links.

## Route B: our client, visiting service

1. Record the visiting service's address, version and access requirements.
2. Inspect its landing page, advertised links, process list and descriptions.
   Ask the owner for a minimal valid input and supported execution modes.
3. Connect our OAP UI to that address using its normal configuration. Follow
   the checklist with the visiting provider's own processes and inputs.
4. Our ZOO/Weaver/DIRECTED cases are patterns, not universal requests. Do not
   merely replace their host and assume the process IDs or schemas will match.
5. Keep new descriptions, requests and outputs as new evidence. New geometry,
   CSV, JSON, file and validation examples are useful even if no automated test
   consumes them yet.

## Record findings without losing existing evidence

Copy [results-template.md](results-template.md), for example to a dated session
folder under `plugfest/`. Give attached requests, responses and screenshots
relative filenames and keep each observation tied to its client/server pair.
For a useful exchange retain method, URL, request headers/body, response status,
headers, final URL and body (or a separate body file). Remove credentials and
session tokens from shared files while retaining the relevant diagnostic data.

Keep new live captures separate from the existing historical scenarios.
In particular, `scripts/run_evidence_request.py --save-response` writes beside
the supplied request and can replace an existing response. Do not use it on an
old scenario as a way to record a new company's server. Afterwards, promote
useful captures into `evidence/<provider>/` with provider metadata and select
only distinct examples for `scenarios/`.

## Where the automated suite fits

`npm run check` runs our recorded tests against the installed OAP core package.
`npm run check:local` runs the same tests against an isolated compilation of
`../oap-client` source. Neither contacts event services, launches the UI, tests
another company's client, or runs the OAP repository's own tests.

These commands are a separate regression check. See the
[current automated coverage](../docs/client-fixture-handoff.md#current-coverage)
and [testing responsibilities](../docs/test-strategy.md#which-repository-tests-what).
