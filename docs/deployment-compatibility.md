# Differences between server deployments

A deployment is one running OGC API - Processes server with a specific set of
software, process plugins, and configuration. Two deployments using the same
server product can expose different processes and responses.

This repository keeps evidence from five deployments under `evidence/`:

- `zoo-local`: the local ZOO server used for most live tests;
- `pygeoapi-demo`: the public pygeoapi demo used for `hello-world`;
- `bgt-prototype`: a local pygeoapi-based BGT process;
- `directed-local`: a local pygeoapi-based CLIMADA process;
- `weaver-redoak`: a public Weaver deployment used for discovery and relay
  evidence.

The three pygeoapi deployments are different because each process plugin defines
its own inputs, outputs, supported execution modes, dependencies, and result
data. Behavior seen in one process should not be assumed for every pygeoapi
server.

The RedOak deployment provides public landing, conformance, and process-list
responses without CORS headers. Its advertised process descriptions returned
HTTP 403 at capture time, so it is not currently used for execution scenarios.
These are properties of that deployment, not defaults for Weaver.

## Why software versions matter

The client only sends HTTP requests, but server upgrades can change those
requests and responses.

| Software change | What may change in the API |
|---|---|
| ZOO-Project | Links, generated schemas, error responses, and job behavior |
| SAGA | Process IDs, parameter IDs, types, allowed values, and outputs |
| OTB | Available applications, conditional parameters, defaults, and outputs |
| GDAL/OGR | Available formats and drivers, options, and defaults |
| PROJ | Available coordinate transformations and numerical results |
| GEOS/CGAL | Exact geometry and topology results |
| Process plugin | The complete process description and result shape |
| Network setup | Whether input and output links are reachable |

SAGA process IDs contain library and numeric tool IDs. Those IDs may refer to
different tools after a SAGA upgrade. OTB applications can also depend on
separately installed modules.

## What the client should do

For each server it connects to, the client should:

1. read the landing-page links and `/conformance` response;
2. fetch the current process list and descriptions;
3. use those descriptions to build and check requests;
4. keep unknown schema fields available as raw JSON;
5. handle new valid error and result shapes without crashing.

A provider update may change a process-specific request without breaking the
generic client. Tests should focus on HTTP behavior, input/output structure,
and usable links. Exact geometry, raster values, filenames, and error messages
may change between versions.

## What to record for a deployment

For useful evidence, record at least:

```text
deployment name and capture date
base URL
process ID
server or processing-library version when known
```

More exact details such as commits, container image digests, conformance
responses, and network settings can be added when investigating a deployment
difference. Their absence should not prevent keeping an otherwise useful
request and response.

## Checking an upgrade

Keep older responses when they explain a relevant difference. Capture selected
descriptions and executions from the upgraded deployment, then compare stable
client-facing properties such as process IDs, inputs, outputs, modes, status,
and links.

Authentication, relays, retries, and server-specific fixes should only be
added when a target server or tender requirement needs them.
