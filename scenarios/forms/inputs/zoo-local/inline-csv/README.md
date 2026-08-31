# Inline CSV inputs

Process: `SAGA.table_tools.3`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/SAGA.table_tools.3/)
- [successful execution](../../../../../evidence/zoo-local/captures/executions/saga_join_tables/)

The request supplies two CSV documents inline. Each input uses a `value`
string and a nested `format` object containing `mediaType: text/csv` and
`encoding: utf-8`. It also includes ordinary Boolean inputs.

A generated form should support multiline text or a CSV file choice, preserve
newlines, and serialize the content with the exact qualified-value wrapper.
Boolean values remain JSON Booleans even though this ZOO description also
lists the strings `true` and `false` in their enums.

The successful recorded execution confirms that ZOO accepted both CSV input
wrappers.

The description does not identify spatial columns, so the CSV should not be
treated as MapLibre data automatically.
