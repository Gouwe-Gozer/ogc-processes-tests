# Local DIRECTED pygeoapi deployment

This local deployment was captured again on 31 August 2026. It ran pygeoapi
`0.25.dev0` and exposed one process:
`climada-simple-example-denmark-process`.

The process is useful because its description and observed behaviour differ:

- array inputs do not describe their item type or length;
- the processor requires exactly three `intensity` values, although that
  restriction is absent from the schema;
- the output is described as an object with `contentMediaType: text/csv`;
- the default synchronous response is actually a raw 18.8 MB CSV body;
- a requested reference response still returned the full CSV inline inside a
  JSON array.

The complete large bodies and compact observations containing their sizes and
SHA-256 hashes are stored under
[`captures/executions/large-csv-output/`](captures/executions/large-csv-output/).

Discovery, the process description, and an asynchronous failed job are stored
under:

- [`captures/discovery/core-discovery/`](captures/discovery/core-discovery/);
- [`captures/descriptions/climada-simple-example-denmark-process/`](captures/descriptions/climada-simple-example-denmark-process/);
- [`captures/jobs/failed-job-undocumented-array-length/`](captures/jobs/failed-job-undocumented-array-length/).

The process description and its undocumented array-length error form the
representative scenario at
[`../../scenarios/forms/validation/directed-local/undocumented-array-length/`](../../scenarios/forms/validation/directed-local/undocumented-array-length/).
