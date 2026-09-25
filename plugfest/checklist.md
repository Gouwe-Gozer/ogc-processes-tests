# Six plugfest checks

Use with the [guide](README.md) and [results sheet](results-template.md).
Start with discovery and a small execution; add the other checks where the
client and server support them. A recorded reply is an example, not a promise
that a different deployment returns identical bytes, timings or job IDs.

For a visiting server, use its own descriptions and example inputs. The process
names below apply only to the corresponding known deployments.

## 1. Connect and discover

- Open the confirmed service in the client and list its processes.
- Open one current description. Can the user identify required inputs, formats
  and outputs? Is a failed description reported without misleading the user?
- Reference: [Weaver discovery](../scenarios/protocol/discovery/weaver-redoak/core-discovery/).
  This is historical public-service evidence, not a guaranteed event endpoint.
- Save the actual landing, listing and description used for subsequent checks.

## 2. Run a small process

- Known ZOO example: `hellojs`, with input `S` set to `Codex`.
  See the [exact request](../scenarios/protocol/execution/zoo-local/simple-sync/01-execute.request.json).
- Alternative pygeoapi example: `hello-world`, with `name` set to
  `OGC API client` and `message` to `Raw response check.`; use its
  [request and response](../scenarios/protocol/execution/pygeoapi-demo/raw-versus-document-response/).
- Check that entered values survive in the outgoing request and the returned
  result is accessible. Keep the actual response rather than assuming a fixed
  greeting across providers.

## 3. Follow a background job

- Known ZOO example: `longProcess`, input `sid: 1`, with async preference.
  Use [successful-job](../scenarios/protocol/jobs/zoo-local/successful-job/).
- Weaver alternative: [EchoProcess successful-job](../scenarios/protocol/jobs/weaver-local/successful-job/).
  Use its full supplied input body; several inputs are required.
- Check that the client finds the returned job address, shows the observed
  status and makes successful results available. Don't expect a new run to
  show every intermediate state seen in a recording.
- If the service immediately returns a result, record that outcome rather than
  declaring that async necessarily happened because it was requested.
- Optional, on a separate running job: request dismissal using
  [the ZOO example](../scenarios/protocol/jobs/zoo-local/dismiss-running-job/).
  Distinguish stopping the local wait from sending DELETE to the server.

## 4. Enter varied input payloads

- Primary example: [Weaver mixed inputs](../scenarios/forms/inputs/weaver-local/mixed-values-map-and-files/).
  Its [complete request](../scenarios/forms/inputs/weaver-local/mixed-values-map-and-files/02-execute.request.json)
  contains enum/date/number values, arrays, ordinary JSON, GeoJSON, bbox and
  inline file data. Enter values through the available controls or documented
  JSON fallback; record which interface was used.
- Smaller alternative: [ZOO inline CSV](../scenarios/forms/inputs/zoo-local/inline-csv/),
  with two text tables and Boolean options in the supplied request.
- Compare the actual request with the intended values. Look for lost zeros or
  false values, changed array structure, lost geometry coordinates, and missing
  media types or encoding. A raw-JSON fallback is distinct from a generated
  form control; record both honestly.

## 5. Inspect varied outputs

- Small spatial example: [ZOO GeoJSON result](../scenarios/results/maps/zoo-local/geojson-value/).
  Confirm any linked input is reachable by the server before using the example.
- Large tabular example: DIRECTED `climada-simple-example-denmark-process`,
  input `intensity: [0, 30, 80]`. See the
  [exact request](../scenarios/results/downloads/directed-local/large-raw-csv/02-execute.request.json)
  and [18.8 MB historical CSV](../scenarios/results/downloads/directed-local/large-raw-csv/).
  A new run may return different contents or size.
- Check what the UI offers: map, text/JSON, table preview, file link or download.
  Record unsupported presentations without treating a valid fallback as a
  protocol error. Large data should remain obtainable without an unusable UI.
- For referenced outputs, try the link from the actual client environment.
  A successful process does not establish that the file is accessible.

## 6. Explain a failure

- With the provider's agreement, use a known failing example such as
  [ZOO failR](../scenarios/protocol/errors/zoo-local/structured-execution-error/).
- A useful validation distinction is
  [DIRECTED's undocumented array length](../scenarios/forms/validation/directed-local/undocumented-array-length/):
  the recorded description allows an array but the recorded provider refuses
  two elements because it needs three. Check the current description first.
- Can the client distinguish local validation, a server refusal and a browser
  access problem? Does it retain the server's useful explanation?
- For a failed background job, a successful status HTTP request does not mean
  the job succeeded: inspect the returned job state.

## Record an outcome for every attempted check

Use: **worked**, **unexpected behaviour**, **unsupported**, **service unavailable**,
**browser/access blocked**, or **not attempted**. “Worked” for the failure check
means that the client handled the expected refusal clearly, not that processing
succeeded. Record the evidence and any uncertainty before attributing a defect.
