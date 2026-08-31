# Array constraint missing from the process description

Process: `climada-simple-example-denmark-process`
Source server: `directed-local`

Original evidence:

- [process description](../../../../../evidence/directed-local/captures/descriptions/climada-simple-example-denmark-process/)
- [failed job](../../../../../evidence/directed-local/captures/jobs/failed-job-undocumented-array-length/)

The process describes `intensity` only as an array. It supplies no `items`,
`minItems`, or `maxItems` schema keywords. A two-element array therefore
matches the published schema, but the provider rejects it with HTTP 400 and
states that exactly three elements are required.

The form layer cannot infer the missing item type or length from the schema.
It should offer raw JSON input for this field rather than inventing validation
rules from the example or description text. An example can help the user, but
it is not a schema constraint.

If the user submits a two-element array, the form should not present it as a
schema-validation error. After the provider rejects it, the UI can show its
message:

```text
Request failed — server message: “Error executing process: The intensity tuple must have three elements, 2 found”
```
