# pygeoapi implementation samples

These recorded-only samples compare pygeoapi's official stable demo with the
unfinished local BGT prototype. They describe two deployments and two process
plugins, not universal pygeoapi process behaviour.

## What pygeoapi supplies

Both deployments expose process descriptions with `jobControlOptions`,
`outputTransmission`, input/output metadata, and typed `self`, `alternate`,
and `execute` links. Both advertise JSON execution URLs containing `?f=json`.
The client should follow those links exactly.

pygeoapi's process-plugin contract makes the plugin responsible for its
metadata, expected inputs and outputs, and returned media type and payload.
Consequently, supported execution modes, schema richness and result content
cannot be inferred from the server product name.

## What differs by deployment or process

| Observation | Official `hello-world` demo | Local BGT prototype | Ownership |
|---|---|---|---|
| pygeoapi version captured | 0.24.0 | 0.23.4 | Deployment |
| Execution modes | sync and async advertised | sync only | Processor metadata plus configured execution support |
| Output transmission | value | value | Processor metadata |
| Inputs | strings plus optional output controls | coordinates and radii | Process plugin |
| Output schema | shallow object declaration | deeply nested closed object | Process plugin |
| Runtime/dependencies | immediate echo | slow live PDOK queries | Process implementation |
| Default response when `response` is omitted | raw processor result | not asserted here | pygeoapi execution handling plus plugin result |
| Document response captured | `outputs` array | output-ID map with qualified `value` | Observed deployment behaviour; do not generalize |

The official demo also advertises the `echo` output as an object while the
captured value is a string. Treat that as an example-process/schema mismatch,
not as a rule for pygeoapi clients.

The BGT sample tests generic parsing and raw-JSON fallback. It does not make
the prototype a conformance oracle, and it does not require the client to
understand BGT-specific fields.
