# Dismiss a running asynchronous job and handle the removed resource

Process: `longProcess`
Source server: `zoo-local`
Selected as [`protocol/jobs/zoo-local/dismiss-running-job`](../../../../../scenarios/protocol/jobs/zoo-local/dismiss-running-job/).

## submit

Handling: `job-accepted`

Expected client handling

- Expose the server-side job independently from the local POST request.

Avoid

- Treat aborting the POST or a polling GET as dismissal of this job.

## dismiss

Handling: `job-dismissed`

Expected client handling

- Expose dismissed as a terminal state and stop polling.
- Preserve the DELETE response as the terminal job document.

Avoid

- Classify dismissal as a network abort or provider failure.
- Fetch results after dismissal.

## get-after-dismiss

Handling: `job-resource-missing`

Expected client handling

- Return the parsed problem with status, headers, final URL, and raw body.
- Do not overwrite a previously observed dismissed state held by the calling
  application.

Avoid

- Recreate or re-submit the job.
- Rewrite the earlier successful dismissal as if it never happened.

## repeat-dismiss

Handling: `dismiss-target-missing`

Expected client handling

- Expose the actual server problem without changing it to the status expected from another implementation.

Avoid

- Automatically retry DELETE after a definitive 404 response.
- Treat the profile deviation as a transport failure.
