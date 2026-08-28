# Immediate provider problem contains useful server detail

Process: `failR`
Source server: `zoo-local`
Selected as [`protocol/errors/zoo-local/structured-execution-error`](../../../../../scenarios/protocol/errors/zoo-local/structured-execution-error/).

## Why it may be useful

- Ordinary synchronous POST returning a structured HTTP problem.
- Representative useful provider detail for safe pass-through presentation.

## execute

Handling: `synchronous-http-problem`

Expected client handling

- Present a request-failed classification with the server message, HTTP status, and raw problem.
- Keep this HTTP failure distinct from an async job whose status later becomes failed.

Avoid

- Translate the R-specific text into a guessed input cause.
- Require a bespoke failR UI message.
- Automatically retry the POST.
