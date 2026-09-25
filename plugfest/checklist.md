# Things to try on a visiting service

Use **our OAP client against the visiting company's service**. Ask its owner
for valid inputs and use its current process descriptions. Try what the service
supports; this is a conversation guide, not a mandatory conformance test.

| Try | What to look for | What is useful to save |
|---|---|---|
| Discover and open a process | Can our client connect, list processes and explain the selected inputs/outputs? | Process description and any discovery problem |
| Execute a small example | Do entered values reach the request correctly, and is the result usable? | Actual request and response |
| Vary the inputs | Do arrays, zero/false values, geometry, JSON, files and references survive the form/encoding? Is JSON fallback clear? | A distinct description/request pair |
| Inspect different outputs | Can the UI make sense of scalar, JSON, GeoJSON, CSV, large data or download links? Are linked files reachable? | Output description, response and any body file |
| Follow a background job, if supported | Can the client find the job, report status and retrieve results? If it finishes immediately, does the client handle that? | Submission, observed status replies and results |
| Try a refusal or dismissal with the owner | Is the explanation useful? Does the client distinguish a failed job from a failed HTTP request, and stopping a wait from dismissing a job? | The request and complete error/dismissal response |

For a useful or unexpected result, write a few lines using the
[results template](results-template.md). Note the client version and service
address. Use Postman/curl for comparison when needed; browser access failures
and unsupported UI features should not automatically be called server defects.

## Our recordings are examples of what to look for

They are not requests to send unchanged to a visiting service:

- [Weaver mixed inputs](../scenarios/forms/inputs/weaver-local/mixed-values-map-and-files/)
  shows why an ordinary JSON object, a geometry and a file need different controls.
- [DIRECTED's undocumented array constraint](../scenarios/forms/validation/directed-local/undocumented-array-length/)
  shows that schema-valid input can still be refused by the provider.
- [DIRECTED's large CSV](../scenarios/results/downloads/directed-local/large-raw-csv/)
  shows why a complete download may be more useful than rendering every row.
- [Weaver sync with job links](../scenarios/protocol/execution/weaver-local/sync-with-job-links/)
  shows that job-related headers do not always mean the client should start polling.

Look for similarly useful differences in the visiting services. A working
example with a new payload shape is worth keeping even when nothing fails.
