# What the client can learn from a process description

A process description tells the client how to build a request for that process.
It can provide:

- the exact process, input, and output IDs;
- titles and descriptions;
- links to the process and execution endpoint;
- support for synchronous execution, asynchronous execution, and dismissal;
- support for output by value or by reference;
- required and optional inputs;
- input types, defaults, allowed values, and minimum or maximum item counts;
- complex input formats, such as GeoJSON, GML, TIFF, or CSV;
- output IDs, types, and formats.

IDs are case-sensitive. Input IDs and output IDs must be stored separately,
because a process may use the same ID for both.

The following values also mean different things:

- **optional**: the input may be left out;
- **nullable**: the request may contain JSON `null`;
- **default**: the server may choose a value when the input is left out.

The client must not lose valid values such as `0`, `false`, or an empty string.

JSON Schema can contain features the client does not understand. In that case,
keep the original schema and allow raw JSON input. Do not ignore unknown rules
and pretend the request was fully checked.

## What the client may assume

For normal form-based requests, use the current process description as the
server's published rules:

- send the IDs shown in the description;
- check the input types and rules the client understands;
- allow an input to be omitted when it is marked optional;
- only offer execution and output modes that are advertised;
- treat advertised media types as the available format choices;
- follow an asynchronous job until it reaches a finished state.

Sometimes a server accepts input that breaks its own description. The client
should still show the validation error in its normal form. Raw JSON input can
be offered as an explicit way to bypass form validation.

## What may still go wrong

### A listed process may not run

The local ZOO server lists several OTB processes and returns valid descriptions
for five of them. Their execution requests still fail with `No OTB Application
found.`. Another listed process, `OTB.ReadImageInfo`, returns HTTP 500 when its
description is requested.

The client should show the server error and keep the other processes usable.
It should not try to repair the server configuration.

### A process may require inputs that it does not describe

`Gdal_Grid` fails when sent only the inputs in its description. Its provider
expects more parameters that are not advertised. One `Gdal_Dem` mode has the
same problem.

The client should not invent hidden inputs. It should send a valid described
request and return the server's error if the provider rejects it.

### Valid data may still be unsupported

A process may advertise a general geometry or file format but only handle part
of it. For example, the tested `Distance` provider rejected point GML while it
accepted polygon GML.

The client can check the JSON structure, wrapper, and media type. It cannot
guarantee that the processing software supports the contents.

### The server may not be able to fetch a URL

An input URL that works in the user's browser may not work from the processing
server. The client can check that the URL is valid, but only the server can say
whether it can download and read the file.

### A string may mean a filename on the server

Some older GDAL and OGR processes describe a file input as a string. That
string is used as a path inside the ZOO server. A path on the user's computer
and a GitHub URL are not valid replacements unless the API provides a separate
upload or download feature.

A description that only says `type: string` cannot prove that the value is a
server filename. Names such as `InputDSN` can be used for a cautious hint in the
UI, but not for automatic behavior.

### HTTP 200 may contain a bad result

Examples in this repository include:

- an empty object even though an output was requested;
- two URLs joined into one invalid string;
- an output link whose file does not exist;
- a path inside the server instead of a downloadable URL.

The client should keep the response, list the outputs it found, and warn when a
requested output is missing or a link cannot be opened. It should not create a
result that the server did not return.

### Error messages may be poor

The server may return a clear message, a generic message, HTML, no useful
detail, or a process crash such as `SIGSEGV` or `SIGABRT`. The crash message
does not tell the client which input caused the problem.

A simple message is enough for this client:

```text
Request failed — server message: “<server detail>”
Job failed — server message: “<job message>”
```

Escape the server text before displaying it. Keep the HTTP status, headers,
final URL, and raw body for inspection. Only blame a specific input when the
server clearly identifies that input.

## Checks before sending input

For the request itself, check:

- that it is valid JSON;
- that `inputs` and `outputs` have the expected object shape;
- that known IDs match the process description;
- that required inputs are present;
- that the chosen execution and output modes are supported;
- that an asynchronous request includes `Prefer: respond-async`.

For schema features the client supports, check:

- JSON value types;
- required versus nullable values;
- allowed values;
- array size and repeated-input limits;
- required properties in nested objects;
- known complex-value wrappers, formats, and encodings.

Do not silently convert, remove, or repair user data. Geometry repair,
coordinate conversion, and checks inside raster/vector files are outside this
client library.

## How to report responses

The client should distinguish:

- no HTTP response, including network failure or abort;
- an HTTP error response;
- a response that should be JSON but is not valid JSON;
- a synchronous result response;
- an accepted, running, successful, failed, or dismissed job;
- failure to download an output link after the process succeeded.

Read OGC error fields such as `title`, `type`, and `detail` when present, but
also keep the original body. Do not automatically retry a process `POST`,
because it may start the work a second time.

## Deeply nested JSON results

The BGT example returns one output containing many nested objects and arrays.
It also contains application fields such as `is_partial`. That field is data
from the process; it is not an OGC job status.

Keep the complete JSON value without flattening it or converting its values.
If there is no special result viewer for it, show it through the raw JSON
fallback.

The pygeoapi `hello-world` example also returns different shapes for a raw
response and a document response. These shapes belong to that process. Other
pygeoapi processes may behave differently.
