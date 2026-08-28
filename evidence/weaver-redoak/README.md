# Public RedOak Weaver deployment

This is a public Weaver deployment operated by the University of Toronto. It
was captured on 27 August 2026.

The landing page, conformance declaration, and process list returned JSON with
HTTP 200. They form the representative discovery scenario at
[`../../scenarios/protocol/discovery/weaver-redoak/basic-discovery/`](../../scenarios/protocol/discovery/weaver-redoak/basic-discovery/).

The capture also found two deployment-specific limitations:

- responses did not include `Access-Control-Allow-Origin`, even when the
  request included an `Origin` header;
- both the unversioned and advertised versioned `EchoProcess` descriptions
  returned HTTP 403 from nginx.

The missing CORS header makes this deployment useful for testing access through
the promised relay transport. The HTTP 403 is separate from CORS: it also
occurs in direct command-line requests. The versioned 403 exchange is stored
under [`responses/`](responses/) and selected as
[`process-description-forbidden`](../../scenarios/protocol/discovery/weaver-redoak/process-description-forbidden/).

These observations describe this deployment at the capture date. They should
not be treated as defaults for every Weaver server. A future local Weaver
deployment should receive its own `evidence/weaver-local/` folder.
