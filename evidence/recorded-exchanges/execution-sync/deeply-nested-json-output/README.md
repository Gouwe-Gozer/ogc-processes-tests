# Synchronous qualified value containing deeply nested JSON

Process: `bgt-land-cover-summary`
Source server: `bgt-prototype`
Stored as supporting evidence; it is not part of the small representative scenario set.

## Why it may be useful

- A qualified output value can contain deeply nested objects, arrays, dynamic property maps, dates, URIs, booleans and numbers.
- Unknown process-specific fields remain intact and available to a raw JSON fallback.
- A domain field named is_partial is data inside the process output, not protocol job state.

## execute

Handling: `synchronous-results-available`

Expected client handling

- Recognize summary as one named qualified output and preserve its complete value object.
- Keep nested objects, arrays, empty objects, booleans, numbers, dates and URI strings without flattening or coercion.
- Make the complete value available to the promised raw JSON fallback when no specialized renderer supports it.

Avoid

- Treat summary.value as a protocol wrapper that may be discarded after extracting only its top-level scalar fields.
- Interpret the process-specific is_partial field as an OGC job status or execution failure.
- Require exact live statistics, timing values, timestamps or object-property order.
