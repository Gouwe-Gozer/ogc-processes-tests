# Job polling returns a syntactically valid but unknown status

Stored as supporting evidence; it is not part of the small representative scenario set.

## poll

Handling: `unknown-job-status`

Expected client handling

- Preserve paused and the complete raw job document as a possible extension value.
- Stop a poll-until-terminal helper with an explicit unsupported-status outcome.

Avoid

- Guess that paused is successful, failed, or dismissed.
- Fetch results or loop forever on an unrecognized status.
- Discard the response because it contains an unknown value.
