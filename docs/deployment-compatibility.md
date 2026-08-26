# Differences between server deployments

A deployment is one running OGC API - Processes server with a specific set of
software, process plugins, and configuration. Two deployments using the same
server product can expose different processes and responses.

This repository records three deployments:

- `zoo-local`: the local ZOO server used for most live tests;
- `pygeoapi-demo`: the public pygeoapi demo used for `hello-world`;
- `bgt-prototype`: a local pygeoapi-based BGT process.

The two pygeoapi deployments are different because each process plugin defines
its own inputs, outputs, supported execution modes, dependencies, and result
data. Behavior seen in one process should not be assumed for every pygeoapi
server.

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
5. tell the user when a saved request no longer matches the description;
6. handle new valid error and result shapes without crashing.

A provider update may change a process-specific request without breaking the
generic client. Tests should focus on HTTP behavior, input/output structure,
and usable links. Exact geometry, raster values, filenames, and error messages
may change between versions.

## What to record for a deployment

For a repeatable test, record:

```text
deployment name and capture date
base URL
server version or commit
container image and immutable digest
processing-library and module versions
process-list hash
conformance response
network or relay settings that affect links
```

An image tag such as `latest` is not enough to prove that two tests used the
same server code.

## Checking an upgrade

1. Add the upgraded server as a new deployment instead of replacing old
   captures.
2. Capture its landing page, conformance response, process list, and selected
   descriptions.
3. Compare process IDs, inputs, outputs, and supported modes.
4. Mark each change as expected, breaking, or a server error.
5. Run the client testcases that the new server can support.
6. Run process-specific probes only when the new description still matches the
   request.
7. Record the results before making the new deployment the main test server.

Authentication, relays, retries, and server-specific fixes should only be
added when a target server or tender requirement needs them.
