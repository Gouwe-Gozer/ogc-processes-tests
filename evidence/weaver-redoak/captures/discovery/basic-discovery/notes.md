# Weaver discovery

Source server: `weaver-redoak`

This scenario contains the public landing page, conformance declaration, and
process list captured from RedOak on 27 August 2026. It covers discovery from
an implementation other than ZOO-Project and pygeoapi.

The protocol core should:

- find the conformance and process-list resources from the landing-page links;
- recognize the declared OGC API Processes conformance classes while ignoring
  additional classes it does not use;
- parse process summaries and preserve their advertised links, including
  versioned process identifiers;
- ignore Weaver-specific fields that are not needed by the core.

The stored `Origin` headers represent headers added by the browser. None of the
responses included `Access-Control-Allow-Origin`, so a browser cannot read them
directly. The same protocol parsing should work when a relay transport supplies
them.

The advertised `EchoProcess` description returned HTTP 403. It is selected as
the separate
[`process-description-forbidden`](../../descriptions/process-description-forbidden/)
capture.
