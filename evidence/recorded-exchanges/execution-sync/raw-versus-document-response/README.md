# Official pygeoapi hello-world description and synchronous responses

Process: `hello-world`
Source server: `pygeoapi-demo`
Stored as supporting evidence; it is not part of the small representative scenario set.

## Why it may be useful

- Compare an official example processor with a custom process on the same server implementation.
- Omitting response produces the processor's raw result, while requesting document produces a different envelope.
- A process description and its observed output can disagree, so raw JSON must remain available.

## get-description

Handling: `process-description-available`

Expected client handling

- Use this process's advertised capabilities and schema rather than applying capabilities observed on another pygeoapi process.
- Preserve the advertised execute link including its query component.

Avoid

- Assume all pygeoapi processes are synchronous-only or have deeply nested outputs.

## execute-default-raw

Handling: `synchronous-raw-result-available`

Expected client handling

- Retain the complete JSON response as the raw output selected by omission of response=document.

Avoid

- Require a document-result envelope for a raw response.

## execute-document

Handling: `synchronous-results-available-with-implementation-variation`

Expected client handling

- Preserve the complete response and make it available through raw JSON fallback.
- Report the advertised object schema and observed string value mismatch if schema validation is performed.

Avoid

- Generalize this outputs-array envelope or schema mismatch to every pygeoapi deployment.
- Crash or discard the response solely because the example processor returns a string where its schema advertises an object.
