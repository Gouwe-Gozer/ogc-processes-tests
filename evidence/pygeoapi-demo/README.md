# Public pygeoapi demo

This deployment points to the public pygeoapi demo captured on 2026-08-25.
The recorded `hello-world` exchanges cover:

- description and execution links containing `?f=json`;
- a raw result when `response` is not supplied;
- a document result when `response: document` is supplied;
- an example where the described output type does not match the returned value.

See [`captures/descriptions/hello-world/`](captures/descriptions/hello-world/)
and
[`captures/executions/raw-versus-document-response/`](captures/executions/raw-versus-document-response/).
The checked-in responses allow the test to run when the public demo is offline.

These results describe `hello-world`, not every process served by pygeoapi.
