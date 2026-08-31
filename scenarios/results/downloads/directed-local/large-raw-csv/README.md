# Large raw CSV result

Process: `climada-simple-example-denmark-process`
Source server: `directed-local`

Original evidence:

- [process description](../../../../../evidence/directed-local/captures/descriptions/climada-simple-example-denmark-process/)
- [raw CSV execution](../../../../../evidence/directed-local/captures/executions/large-csv-output/)
- [recorded 18.8 MB CSV body](../../../../../evidence/directed-local/captures/executions/large-csv-output/01-execute-raw.body.csv)

This is a raw result. The HTTP body itself is the CSV semantic payload; there
is no output ID, `value` wrapper or JSON result document. The response's
`Content-Type: text/csv` identifies it.

The UI should offer the complete response as a download. It may show a limited
or paginated table preview, but should not eagerly render all rows. The
scenario response points to the body stored under evidence so the 18.8 MB file
is not duplicated.
