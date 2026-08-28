# Raw and document results from pygeoapi

Process: `hello-world`
Source server: `pygeoapi-demo`

This scenario contains a process description followed by two synchronous
executions:

- omitting `response` produces the process's raw result;
- requesting `response: document` produces an outputs envelope.

It also records a mismatch between the advertised object output and the string
value returned by this process.

The protocol core should preserve the exact execute link, including its query,
and accept both result modes without assuming that every pygeoapi process uses
the same response shape. When the observed value does not match the advertised
schema, it should remain available through the raw JSON fallback.

These files were captured from the public pygeoapi demo on 25 August 2026.
