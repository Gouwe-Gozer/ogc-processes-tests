# Advertised job list returns HTTP 403

Captured from `weaver-redoak` on 31 August 2026.

The landing page advertises the global job-list URL, but a direct GET returned
an nginx HTTP 403 HTML response. The same response was returned for an unknown
job URL, so no separate unknown-job capture was kept.

This does not prove that Weaver has no jobs or does not support job listing. It
shows that this deployment does not allow anonymous access to those resources.
A browser also cannot read the response directly because it has no CORS
permission header. A relay can return the HTTP 403 to the client.
