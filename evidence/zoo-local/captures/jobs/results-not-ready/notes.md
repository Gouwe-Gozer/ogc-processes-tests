# Results are requested before the job reaches successful

Process: `longProcess`
Source server: `zoo-local`
Stored as supporting evidence; it is not part of the small representative scenario set.

## submit

Handling: `job-accepted`

Expected client handling

- Retain the non-terminal job state.

Avoid

- Issue the next results request during ordinary client operation; it is deliberately premature.

## get-results-too-early

Handling: `results-not-ready`

Expected client handling

- Expose the OGC problem detail while retaining the job as non-terminal.
- Direct the lifecycle back to job-status retrieval rather than repeating the result request.

Avoid

- Classify the job itself as failed from this 404.
- Treat the missing result resource as a network failure.
- Return an empty successful result.

## cleanup

Handling: `job-dismissed`

Expected client handling

- Use DELETE to clean up the timing-sensitive test job.

Avoid

- Confuse cleanup dismissal with the earlier ResultNotReady problem.
