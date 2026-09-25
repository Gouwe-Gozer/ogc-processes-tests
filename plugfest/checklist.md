# Service probes

First capture a small request that works. Use the service's own process
identifiers and description. Save each variation separately so the provider
can reproduce it without our UI. Start with small workloads; agree potentially
expensive or deliberate failure cases with the owner.

| Probe | How to try it | What to inspect |
|---|---|---|
| Discovery and descriptions | Follow advertised process and description links | Are links reachable? Do the listed IDs match the descriptions? |
| Required and optional inputs | Omit one required input; separately omit one optional input | Does behaviour match the description? Is a refusal understandable? |
| Types and constraints | Vary one declared number range, enum, item count or value type | Distinguish expected validation errors from crashes or undocumented restrictions |
| Values easy to lose | Submit valid `0`, `false`, arrays, or an empty string where allowed | Compare the actual request with what the user entered, then inspect the response |
| Formats and output selection | Request one of the process's advertised formats or output modes | Does the returned media type/body match? Is the requested output present? |
| Background execution | Request async if supported; follow the returned job address | Does status remain accessible and lead to a result or explained failure? An immediate result is an observation, not automatically a defect |
| Result links | Follow the actual output references returned | Are files reachable, and do their types/content match the advertised output? |
| Dismissal | Dismiss a running test job if supported, then read status | Record the actual terminal response or missing-resource reply; do not assume one shape across providers |
| Browser access | Compare the browser request with the same direct HTTP request | Record preflight failure or inaccessible response headers separately from process failure |

For a suspected problem, keep: valid baseline, changed request, actual reply,
expected behaviour and its basis. Use the [report template](results-template.md).
A non-2xx response to invalid input is not by itself a failure of the service.

Also retain successful input/output variations for UI work. Our
[Weaver mixed values](../scenarios/forms/inputs/weaver-local/mixed-values-map-and-files/),
[DIRECTED array constraint](../scenarios/forms/validation/directed-local/undocumented-array-length/)
and [large CSV](../scenarios/results/downloads/directed-local/large-raw-csv/)
illustrate useful shapes and differences; their requests are not portable to
an unrelated provider just by replacing the host.
