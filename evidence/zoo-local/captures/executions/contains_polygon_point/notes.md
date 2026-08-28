# Ordered geometry references produce a Boolean result

Process: `Contains`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative scenario set.

## Why it may be useful

- Direction-sensitive ordered inputs.
- Inline Boolean output.

## execute

Handling: `synchronous-results-available`

Expected client handling

- Preserve InputEntity1 and InputEntity2 as distinct ordered fields.
- Expose the result as a Boolean without string conversion.

Avoid

- Swap geometry inputs based on labels or geometry type.
- Treat false as a missing result in a future response.
