# Advertised repeated raster input

Process: `SAGA.grid_tools.0`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/SAGA.grid_tools.0/)
- [successful singleton execution](../../../../../evidence/zoo-local/captures/executions/saga_resample_rasters/)
- [failed repeated execution](../../../../../evidence/zoo-local/captures/executions/saga_resample_rasters_repeated_input_expected_error/)

The description advertises up to 1024 `INPUT` values. The recorded repeated
request therefore supplies an array containing:

1. an AAIGrid file referenced by `href` and `type`;
2. an AAIGrid value supplied inline as base64 with a nested `format` object.

ZOO returned HTTP 500 with a SIGSEGV detail for the repeated request, although
a singleton referenced input was processed successfully.

The form and serializer should allow repetition, retain the item order, and
preserve each item's own link or inline representation. They should not reject
the request based on this provider failure. The client can present the failure
as a server error after submission.

The repeated values need an add/remove file-or-URL control. Neither AAIGrid
entry is a direct MapLibre source without an additional raster conversion step.
