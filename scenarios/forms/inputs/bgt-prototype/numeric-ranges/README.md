# Numeric ranges and defaults

Process: `bgt-land-cover-summary`
Source server: `bgt-prototype`

Original evidence:

- [process description](../../../../../evidence/bgt-prototype/captures/descriptions/bgt-land-cover-summary/)
- [successful execution](../../../../../evidence/bgt-prototype/captures/executions/deeply-nested-json-output/)

The description contains required latitude and longitude numbers with minimum
and maximum values. It also contains optional integer radii with defaults and
ranges. The execution request supplies all four values directly under their
input IDs and accepted the recorded request.

A generated form should:

- distinguish numbers from integers;
- mark latitude and longitude as required;
- apply the advertised minimum and maximum values;
- show the radius defaults without making the optional fields required; and
- serialize the values as JSON numbers, not strings.

The deeply nested execution result is not the form assertion in this scenario.
It is retained because it proves that the captured input body was accepted.

Latitude and longitude are separate numeric inputs, not an advertised GeoJSON
Point. A generic client should not combine them into a MapLibre point control
without an application-specific rule.
