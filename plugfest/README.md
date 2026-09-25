# Plugfest: try other companies' services

**Our main goal is to connect our OAP client to other companies' OGC API
Processes services.** Find out what works, where our client struggles, and
collect new request/output examples for the core and UI.

Testing another company's client against our local APIs is an optional extra.
It does not need to be organised before we can start testing services.

## Get started with a visiting service

1. **Ask for the service URL and one working example.** Get a process ID and
   valid inputs from its owner, plus access details if needed.
2. **Open the service in our OAP client.** Browse its processes, open the chosen
   description, enter the example inputs and execute it.
3. **Look at the request and result.** Did the form make sense? Did the request
   contain the intended values? Can the user understand or use the output?
4. **Save anything interesting.** Keep the process description, actual request
   and response, and a short note. Use the [small results template](results-template.md)
   if helpful. Follow the [checklist](checklist.md) for further things to try.

There is no endpoint inventory to complete first. Use the service and examples
available at the event. Start with one successful execution, then explore
interesting inputs, outputs, jobs and errors with the service owner.

## If something does not work

Try the same request directly in Postman or curl. Keep the actual method, URL,
headers and body so the comparison is meaningful. If direct HTTP succeeds but
the browser fails, inspect the browser's network/console output: access or CORS
may be the difference. Direct HTTP success alone does not prove UI compatibility.

For a new service, build the request from its current description and the
owner's example. Our existing Postman requests are useful references, but
changing a ZOO or Weaver base URL does not make their process IDs and inputs
valid for another provider.

## What we want to bring home

New, useful examples matter as much as a pass/fail result:

- Input descriptions and request bodies that exercise forms: arrays, enums,
  GeoJSON, nested JSON, CSV, inline files or references.
- Output descriptions and responses with different values, wrappers, media
  types, sizes and download links.
- Errors or job responses that our client does not explain or handle well.

Save new captures in a separate dated folder, with a short service/process note.
Retain request method/URL/headers/body and response status/headers/final URL/body;
keep large bodies as separate files. Remove credentials from shared copies.
Do not overwrite the old recordings with an event run. Afterwards we can curate
useful examples into `evidence/` and `scenarios/`, and add focused tests.

## Optional extra: another company's client against our local APIs

Visitors can run the local APIs themselves using the container instructions
in the repositories on [Minert's GitHub page](https://github.com/Gouwe-Gozer).
Those setups are intended to match the addresses used by this test repository.
Use each API repository's README to start it; no shared event deployment is
required. This test repository itself does not start the containers.

Once an API is running, connect the visiting client and use our
[existing scenarios](../scenarios/) as examples. Import the
[representative Postman collection](../generated/postman/representative-scenarios.postman_collection.json)
for the corresponding requests and recorded responses. If a local port/address
was changed, adjust the provider's collection variable in the imported copy.

Useful starting points are [ZOO hellojs](../scenarios/protocol/execution/zoo-local/simple-sync/),
[Weaver's mixed inputs](../scenarios/forms/inputs/weaver-local/mixed-values-map-and-files/)
and [DIRECTED's large CSV](../scenarios/results/downloads/directed-local/large-raw-csv/).
For job sequences, run the specific successful-job folder rather than the whole
collection. See the [Postman notes](../generated/postman/README.md) for details.

## The automated suite is a separate tool

`npm run check` and `npm run check:local` replay saved responses against our
core client. They do not contact the visiting service, launch a UI or run another
company's client. New event captures can become future regression tests; see
[current automated coverage](../docs/client-fixture-handoff.md#current-coverage).
