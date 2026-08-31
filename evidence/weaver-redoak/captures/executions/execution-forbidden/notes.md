# Advertised execution endpoint returns HTTP 403

Captured from `weaver-redoak` on 31 August 2026.

The public process list advertises `EchoProcess` and its execution endpoint,
but the process description is already inaccessible. This request deliberately
used an empty JSON body so it could not start a valid process execution.

The endpoint returned the same nginx HTTP 403 HTML response as the description,
job list, and CORS preflight. This indicates that the deployment blocks the
request before Weaver validates the execution body. It should not be presented
as invalid end-user input or treated as normal Weaver execution behaviour.
