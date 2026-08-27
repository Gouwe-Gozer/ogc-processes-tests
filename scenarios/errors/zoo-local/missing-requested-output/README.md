# HTTP success omits the requested repeated output

Process: `SAGA.grid_tools.27`
Source server: `zoo-local`

The request asks for output `TILES`, but the server returns HTTP 200 with an
empty JSON object.

The protocol core should retain the raw response and keep HTTP success separate
from result completeness. It must not invent an empty output or claim that the
requested result was returned.
