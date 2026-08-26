# Accepted submission has no Location header but has a usable monitor link

Stored as supporting evidence; it is not part of the small representative example set.

## submit

Handling: `job-accepted-with-protocol-warning`

Expected client handling

- Find the monitor link by relation and resolve its root-relative href against the final submission URL.
- Expose the accepted job and retain that the required Location header was absent.

Avoid

- Reject a usable job solely because the fallback monitor link is in the body.
- Match the link by human-readable title or array position.
