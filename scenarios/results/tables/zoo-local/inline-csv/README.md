# Inline CSV table

Process: `SAGA.table_tools.3`
Source server: `zoo-local`

Original evidence:

- [process description](../../../../../evidence/zoo-local/captures/descriptions/SAGA.table_tools.3/)
- [successful execution](../../../../../evidence/zoo-local/captures/executions/saga_join_tables/)

The CSV text and its media type are:

```text
body.RESULT.value
body.RESULT.format.mediaType
```

The UI can parse this small UTF-8 CSV as a table and should also offer it as a
download. The CSV string itself is the semantic payload; `RESULT`, `value` and
`format` are result-document wrappers.
