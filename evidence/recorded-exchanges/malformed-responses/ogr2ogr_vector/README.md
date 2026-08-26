# HTTP success contains a malformed URL-like literal

Process: `Ogr2Ogr`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative example set.

## Why it may be useful

- Literal output that visually resembles a URL.
- Successful HTTP envelope whose content is not safely usable as a reference.

## execute

Handling: `synchronous-result-with-warning`

Expected client handling

- Preserve and display the literal string exactly as returned.
- Keep the HTTP execution success separate from whether a consumer can use the value.

Avoid

- Treat every string containing http as a reference wrapper.
- Automatically fetch or repair the concatenated URL.
- Change the returned literal into a guessed provider URL.
