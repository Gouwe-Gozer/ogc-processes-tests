# Array constraint missing from the process description

Process: `climada-simple-example-denmark-process`
Source server: `directed-local`

The process describes `intensity` only as an array. It supplies no `items`,
`minItems`, or `maxItems` schema keywords. A two-element array therefore
matches the published schema, but the provider rejects it with HTTP 400 and
states that exactly three elements are required.

The form layer cannot infer the missing item type or length from the schema.
It should offer raw JSON input for this field rather than inventing validation
rules from the example or description text. An example can help the user, but
it is not a schema constraint.

The protocol core should send input accepted by the published contract and, if
the provider rejects it, return the HTTP status and server description. A
suitable user-facing message is:

```text
Request failed — server message: “Error executing process: The intensity tuple must have three elements, 2 found”
```

The HTTP 400 response also contains a `Location` header for a failed job record.
The client should preserve that header for diagnostics, but it must not treat
the request as an accepted asynchronous job: the response status is 400, not
201.
