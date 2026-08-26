# Repeated images and overlapping input/output IDs reach an unavailable runtime

Process: `OTB.BandMath`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative example set.

## Why it may be useful

- Repeated inline base64 image inputs.
- The ID out occurs separately in inputs and outputs and must not collide.

## execute

Handling: `synchronous-http-problem`

Expected client handling

- Keep inputs.out and outputs.out in separate namespaces when validating and serializing.
- Allow the description-conformant request and safely display the unavailable-runtime detail.

Avoid

- Overwrite the input selection with the output request because both use out.
- Blame the TIFF fixture when direct OTB CLI validation succeeded.
- Build OTB-specific recovery or retry behaviour into the client.
