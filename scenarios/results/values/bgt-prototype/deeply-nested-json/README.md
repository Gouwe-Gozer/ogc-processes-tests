# Deeply nested JSON result

Process: `bgt-land-cover-summary`
Source server: `bgt-prototype`

Original evidence:

- [process description](../../../../../evidence/bgt-prototype/captures/descriptions/bgt-land-cover-summary/)
- [successful execution](../../../../../evidence/bgt-prototype/captures/executions/deeply-nested-json-output/)

The semantic payload is the ordinary JSON object at:

```text
body.summary.value
```

It contains nested objects, dictionaries, arrays, numbers, Booleans, URLs and
date-time strings. It is not GeoJSON and should not be sent to MapLibre merely
because the HTTP response is JSON.

A generic client can show a structured JSON view and offer the original JSON
as a download. Domain-specific cards or tables are optional enhancements; the
client should not flatten this object automatically and lose its hierarchy.
