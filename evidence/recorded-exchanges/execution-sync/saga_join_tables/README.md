# Two inline UTF-8 CSV values produce inline CSV

Process: `SAGA.table_tools.3`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative example set.

## Why it may be useful

- Multiple inline textual complex inputs with format and encoding.
- Inline CSV output kept as text by the protocol core.

## execute

Handling: `synchronous-results-available`

Expected client handling

- Preserve input newlines, media type, encoding, and the returned CSV text.
- Expose the declared text/csv format to the consumer.

Avoid

- Parse CSV into an application-specific table model inside the protocol core.
- Trim or normalize the returned complex text value.
