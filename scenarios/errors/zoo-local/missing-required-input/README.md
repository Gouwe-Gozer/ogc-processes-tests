# Required hellojs input is omitted

Process: `hellojs`
Source server: `zoo-local`

The request omits required input `S`. ZOO returns HTTP 400 with a structured
`MissingParameterValue` problem that identifies the input.

Future form validation should normally prevent this request. The protocol core
must still preserve and parse the HTTP response when invalid JSON is submitted
through a raw-input path or by another caller.
