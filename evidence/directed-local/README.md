# Local DIRECTED pygeoapi deployment

This local deployment was captured on 27 August 2026. It ran pygeoapi
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

The large bodies are not checked into Git. Their response metadata, sizes, and
SHA-256 hashes are stored under
[`exchanges/execution-sync/large-csv-output/`](exchanges/execution-sync/large-csv-output/).

The process description and its undocumented array-length error form the
representative scenario at
[`../../scenarios/validation/directed-local/undocumented-array-length/`](../../scenarios/validation/directed-local/undocumented-array-length/).
