# Simple synchronous execution

Process: `hellojs`
Source server: `zoo-local`

This is the smallest successful synchronous execution in the representative
set. It sends one string input and receives one string result in the HTTP 200
response.

Use it as the basic protocol test for sending an execution request, recognising
an immediate result, and preserving the response. More complicated input and
output shapes belong in the form and result scenarios.

The source exchange remains under
[`evidence/zoo-local/exchanges/execution-sync/hellojs_string/`](../../../../../evidence/zoo-local/exchanges/execution-sync/hellojs_string/).
