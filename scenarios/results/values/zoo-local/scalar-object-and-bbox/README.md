# Scalar, object and bounding-box outputs

Process: `EchoProcess`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/EchoProcess/)
- [successful execution](../../../../../evidence/zoo-local/captures/executions/echo_all_input_kinds/)

One result document demonstrates three output placements:

```text
body.literalOutput
body.complexOutput.value
body.c
```

The first is a direct string, the second is a qualified ordinary JSON object,
and the third is a bounding box with `bbox` and `crs`. The UI should render the
string as text, retain the object as JSON, and may draw the bounding box as a
rectangle after checking its CRS.

Output objects must be classified using the output description and known
result wrappers. The client must not unwrap every object that happens to have
a property named `value`.
