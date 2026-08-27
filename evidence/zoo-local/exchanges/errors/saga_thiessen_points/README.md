# Description-conformant vector request terminates with SIGABRT

Process: `SAGA.shapes_points.16`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative scenario set.

## Why it may be useful

- Referenced point FeatureCollection plus numeric literal.
- Provider abort after a valid execution envelope.

## execute

Handling: `synchronous-http-problem`

Expected client handling

- Treat the problem as a server/provider failure and safely pass through its detail.
- Keep the accepted reference wrapper available for inspection.

Avoid

- Convert SIGABRT into an input-validation error.
- Promise that every advertised geometry subtype is implemented.
- Automatically retry the execution.
