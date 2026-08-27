# Structured execution error

Process: `failR`
Source server: `zoo-local`

The synchronous execution returns HTTP 500 with a JSON problem containing
`title`, `type`, and provider detail.

The protocol core should return the HTTP response and parsed problem rather
than treating it as a network failure. The application can display the server
detail safely without adding process-specific recovery or retry behaviour.
