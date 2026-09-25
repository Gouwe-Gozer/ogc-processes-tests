# Read an unknown job

Source server: `weaver-local`
Source captures: [unknown-job evidence](../../../../../evidence/weaver-local/captures/jobs/unknown-job/).

A GET for the all-zero job ID returns HTTP 404 with a structured `NoSuchJob`
problem. The request and response are copied unchanged from the evidence.
There is no earlier running job in this recording: do not describe it as a
job disappearing or being dismissed.

The client's `getJob` call should reject with `JobNotFoundError`, preserving
the server problem as its cause. It should not turn this into a successful
status, retry, or create a replacement job. The related ZOO dismissal scenario
covers how the polling API handles a missing resource differently.
