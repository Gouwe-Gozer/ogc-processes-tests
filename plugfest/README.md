# Using this repository at the plugfest

Use the recordings, Python capture scripts and Postman collections to collect
examples, investigate services and help client developers reproduce problems.
Run the commands below from the root of `ogc-processes-tests`.

## 1. Collect evidence for our client

Keep a process description together with the request sent and the reply
received. Successful examples are useful too: different arrays, GeoJSON, CSV,
JSON wrappers and files help us build and test forms and result presentation.

### Add the service

Choose a new provider folder, for example `evidence/plugfest-example`:

```bash
mkdir -p evidence/plugfest-example/captures/discovery
```

Create `evidence/plugfest-example/server.json` with the following content.
Replace the example address and title with the actual service details:

```json
{
  "id": "plugfest-example",
  "title": "Company / service name",
  "base_url": {
    "variable": "plugfestExampleBaseUrl",
    "default": "https://service.example.invalid/api"
  }
}
```

The `id` must match the folder name. Keep versions and capture dates in the
notes when known. Use a different folder for a different deployment.

### Capture an exchange

Create `evidence/plugfest-example/captures/discovery/01-landing.request.json`:

```json
{
  "method": "GET",
  "url": "{{baseUrl}}/",
  "headers": { "Accept": "application/json" }
}
```

Inspect the request as curl without sending it:

```bash
python3 scripts/run_evidence_request.py \
  evidence/plugfest-example/captures/discovery/01-landing.request.json \
  --server plugfest-example --print-curl
```

Send it and save the complete reply:

```bash
python3 scripts/run_evidence_request.py \
  evidence/plugfest-example/captures/discovery/01-landing.request.json \
  --server plugfest-example --save-response
```

This writes `01-landing.response.json` with status, headers, final URL and body.
Large/binary bodies go into a separate file referenced by `body_file`. HTTP
error replies are saved too; a network failure has no HTTP response to save.
The script's exit code alone is not a verdict on the service: inspect the reply.

Follow the landing page's advertised links to capture the process list and a
process description. For each next exchange, create another request file with
the same format. Use the actual URL; for a POST add a `body` containing the JSON
request accepted by that process. Start with a working example from its owner.
Use unique filenames for variants and status snapshots: `--save-response`
replaces the response paired with the supplied request.

The capture script sends one request at a time. It does not discover processes,
poll jobs or fill job variables automatically. For job/status/result requests,
put the actual address from the previous reply in the next request file.
`{{baseUrl}}` is supported in the request URL; other placeholders and variables
inside request bodies are not expanded by this script.

If the request was made by a UI, also save its actual outgoing request from the
browser network panel. A separate script run is a comparison, not evidence of
what the UI sent. Remove credentials from shared captures.

### Make the evidence usable

Add a short `notes.md` beside the exchange: what input was used, what happened,
and why the payload is interesting. Use the [notes template](results-template.md)
for an issue that needs follow-up. Keep the original payload and link related
files rather than rewriting it to match our client's expectations.

Generate a Postman collection for the new provider:

```bash
python3 scripts/generate_postman_collections.py
```

Import `generated/postman/evidence/plugfest-example.postman_collection.json`.
Its `baseUrl` variable comes from `server.json`. Evidence collections support
manual inspection; they do not automatically follow job sequences.

After the event, select distinct examples for `scenarios/forms/`,
`scenarios/results/` or `scenarios/protocol/`. Collection does not automatically
create an executable test. Our current tests and their scenario links are
listed in [current coverage](../docs/client-fixture-handoff.md#current-coverage).

## 2. Probe a service and report reproducible problems

Start with the provider's working example. Use our OAP UI to see how it behaves
for a user, and Postman or the capture script to inspect HTTP directly.
Then use the [probe checklist](checklist.md), changing one thing at a time.

For each variation, save a separate request and response. Compare what the
service advertises with what it actually accepts and returns. Useful findings
include a declared required input being ignored, an advertised result link
that fails, an output contradicting its description, or a job that becomes
unreachable. An intentional invalid-input rejection is not itself a defect.

Before reporting an issue:

1. Repeat the smallest request that demonstrates it directly, without the UI.
2. State what you expected and why: the process description, an advertised
   link, or the behaviour agreed with the provider. Distinguish that from a UI
   preference or an unsupported feature.
3. Share the request/curl command, response, service address, process ID and
   observation time. Include the valid baseline when reporting a variation.

If Postman succeeds but the web client cannot access the reply, record the
browser/page URL and network/console details. CORS and header visibility need
browser evidence. Do not label a difference a server or client defect before
checking which part failed. The [notes template](results-template.md) keeps
this report short.

## 3. Help another company test its client

### Use a running API and the existing examples

The other team can start our local APIs using the container instructions in
the repositories on [Minert's GitHub page](https://github.com/Gouwe-Gozer).
Those setups use addresses recognised by this repository. Connect their
client to the API they started and import our
[representative Postman collection](../generated/postman/representative-scenarios.postman_collection.json)
for reference requests and recorded replies.

| Example | What their client can try |
|---|---|
| [ZOO hellojs](../scenarios/protocol/execution/zoo-local/simple-sync/) | Submit `S: "Codex"` and show the immediate result |
| [Weaver mixed inputs](../scenarios/forms/inputs/weaver-local/mixed-values-map-and-files/) | Build a request from varied form controls or JSON input |
| [Weaver background job](../scenarios/protocol/jobs/weaver-local/successful-job/) | Find the job address, read status and retrieve results |
| [DIRECTED large CSV](../scenarios/results/downloads/directed-local/large-raw-csv/) | Handle a large raw response and offer useful output access |

If addresses changed, set `zooLocalBaseUrl`, `weaverLocalBaseUrl` or
`directedLocalBaseUrl` in the imported representative collection. Inspect any
absolute input/output links too. Use the current process description and new
job IDs. Run a selected job folder in Collection Runner to use its scripts;
those scripts are included in the representative collection, not the evidence
collections. See the [Postman instructions](../generated/postman/README.md).

Have their client construct the request, then compare it with the example.
Save differences in values, encoding, job handling or presentation. This route
requires no changes to our TypeScript tests.

### Reuse recordings in their automated tests

The JSON recordings and body files are independent of the client library.
Their developers can use them as fixtures in their own tests:

1. Select a request/response pair and its description, if relevant.
2. Call their real client with the selected inputs.
3. Supply the recorded status, headers and body through their client's supported
   HTTP test mechanism, preserving `final_url` where applicable.
4. Check the request it builds and the result or error it returns.

Use the value inside a response capture's `body`, not the entire capture object,
as the HTTP body. For `body_file`, load the referenced bytes. Preserve links to
our scenario and original evidence when copying fixtures.

Our current `tests/` imports `@breinstein/oap-client` and asserts its public
return types. Neither changing a base URL nor running `check:local` selects a
different company's library. Adapting executable tests requires their developers
to connect their public calls and HTTP test mechanism and write assertions for
their return values. The [recorded fetch helper](../tests/support/recorded-fetch.ts)
is a small example, not a universal adapter. For a UI-only client, use the live
API walkthrough above or their own browser automation.

`npm run check` and `npm run check:local` remain offline checks of our OAP core.
They do not probe a live service or run another company's client.
