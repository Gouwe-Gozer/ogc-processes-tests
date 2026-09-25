# Plugfest results: CLIENT NAME against SERVICE NAME

Copy this file for each client/server combination. Use relative links to files
saved alongside it. Do not fill unknown details with guesses.

## Session

- Date/time and timezone:
- Tester and organisation:
- Route: visiting client → known service / our client → visiting service
- Client name, version or commit:
- Client page URL (or command/tool version):
- Browser and version, if applicable:
- Server implementation/version, if known:
- Service base URL:
- Direct connection or proxy/relay (include address/version where relevant):
- Access requirements (no passwords/tokens):
- Provider contact or reference:

## Checklist summary

| Check | Process ID | Outcome | Observation / evidence link |
|---|---|---|---|
| 1. Connect and discover | | | |
| 2. Small execution | | | |
| 3. Background job | | | |
| 4. Varied inputs | | | |
| 5. Varied outputs | | | |
| 6. Failure handling | | | |

Outcomes: worked / unexpected behaviour / unsupported / service unavailable /
browser/access blocked / not attempted. A test expecting a refusal can work.

## Observation (repeat for each useful case)

- Check number and process ID:
- Description used (saved file/link, time fetched):
- Existing scenario used as a reference, if any:
- Values entered, chosen formats and execution mode:
- UI controls used, including any raw-JSON fallback:
- Steps to reproduce:
- Expected observation and its basis (description, specification, agreed feature):
- Actual observation:
- Outcome and uncertainty:

### Request and response evidence

- Actual client request: method, URL, headers and body file:
- Actual response: status, headers, final URL and body/body-file:
- Job address/ID, observed states, results address and timing, if applicable:
- Direct Postman comparison: same request or differences; result/evidence:
- Browser console/network evidence, including preflight if relevant:
- Screenshots or recording:
- Credentials/tokens removed before sharing:

If browser access failed, note which details were actually available. Don't
substitute a Postman response for a response the browser could not read.

### UI and follow-up

- Input/form issue or useful input variation:
- Output shape/media type/size and presentation offered:
- Referenced files reachable? Download usable? Preview responsive?
- Is this a distinct example worth retaining under `evidence/` or `scenarios/`?
- Suspected layer: client / server / deployment-access / unknown, and why:
- Agreed follow-up, owner and issue link:

Keep new captures separate from existing historical recordings. A surprising
result is an observation to investigate, not automatically a compliance failure.
