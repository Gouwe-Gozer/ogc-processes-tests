# Successful Weaver process description

Process: `EchoProcess`
Source server: `weaver-local`

This scenario supplies a successful process description from Weaver. Its
`inputs` and `outputs` are objects keyed by identifier and include primitive,
array, bounding-box, binary, JSON, and geospatial schemas.

The protocol core should return the description without assuming the exact
layout used by ZOO-Project or pygeoapi. Form-generation tests can later reuse
the same description for its varied input definitions.

The source exchange remains under
[`evidence/weaver-local/captures/descriptions/EchoProcess/`](../../../../../evidence/weaver-local/captures/descriptions/EchoProcess/).
