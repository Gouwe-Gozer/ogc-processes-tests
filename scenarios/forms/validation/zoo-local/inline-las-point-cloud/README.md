# Inline LAS point-cloud input

Process: `SAGA.pointcloud_tools.4`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/SAGA.pointcloud_tools.4/)
- [execution failure](../../../../../evidence/zoo-local/captures/executions/saga_pointcloud_to_grid/)

The request supplies a LAS file inline as base64 with a nested `format` object,
plus enum and numeric controls. This matches the advertised wrapper and media
type, but ZOO terminates with a SIGSEGV and returns HTTP 500.

The form may offer a LAS file input and serialize it as recorded. MapLibre does
not directly display LAS point clouds; previewing one would require a separate
point-cloud library or conversion. The client should show the provider error
without claiming that successful base64 encoding proves the LAS content is
processable.
