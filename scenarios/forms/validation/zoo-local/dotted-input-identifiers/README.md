# Input identifiers containing dots

Process: `OTB.Segmentation`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/OTB.Segmentation/)
- [execution failure](../../../../../evidence/zoo-local/captures/executions/otb_segmentation/)

The description contains input IDs such as `filter.meanshift.spatialr`,
`mode.vector.neighbor`, and `mode.raster.out`. They are flat input identifiers,
not paths into nested JSON objects. The request also demonstrates an inline
base64 TIFF value with an explicit media type and encoding.

A generated form should use the advertised titles and descriptions for labels,
but serialize every value under its exact input ID. It must not turn the dots
into nested objects.

This process is useful as a description and serialization fixture. The local
OTB application module was unavailable at execution time, so the captured
HTTP 500 response is not proof of successful processing. A form test should
compare the generated request with the recorded request; a live success test
should not use this process.

The TIFF is a generic file input for this form. It is not a direct MapLibre
source, and the dotted identifiers do not change map behaviour.
