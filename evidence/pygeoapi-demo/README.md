# Public pygeoapi demo

This deployment points to the public stable pygeoapi demo, captured again on
31 August 2026. The recorded `hello-world` exchanges cover:

- description and execution links containing `?f=json`;
- a raw result when `response` is not supplied;
- a document result when `response: document` is supplied;
- an example where the described output type does not match the returned value;
- an async preference that the provider answers synchronously with HTTP 200
  and `Preference-Applied: wait`.

See [`captures/discovery/core-discovery/`](captures/discovery/core-discovery/),
[`captures/descriptions/hello-world/`](captures/descriptions/hello-world/),
[`captures/executions/raw-versus-document-response/`](captures/executions/raw-versus-document-response/),
and [`captures/jobs/`](captures/jobs/).
The checked-in responses allow the test to run when the public demo is offline.

These results describe `hello-world`, not every process served by pygeoapi.
