# Dismiss a running job, then access its removed resource

Process: `longProcess`
Source server: `zoo-local`
Source captures: [dismiss-running-job evidence](../../../../../evidence/zoo-local/captures/jobs/dismiss-running-job/).

The scenario submits an asynchronous job and sends `DELETE` to the returned job
URL while it is running. ZOO returns a terminal job document with status
`dismissed`. A subsequent `GET` and a repeated `DELETE` both return HTTP 404
with a `NoSuchJob` problem. The last two exchanges are copied unchanged from
the supporting evidence; they are not newly captured or simulated replies.

The client should preserve the successful dismissal. Its `pollJob` function
reports a later missing resource as `dismissed-remotely`, while a repeated
`dismissJob` call rejects with the actual HTTP problem. Neither operation
should resubmit the process, retrieve results, or retry after the definitive
404. The tests explicitly make these later calls; dismissal does not start a
poll loop itself.

The API label `dismissed-remotely` is the client's interpretation of a 404.
A missing job alone does not prove why it disappeared. In this recorded
sequence the preceding successful DELETE supplies that context. This is not
a recording of a job disappearing during a concurrent poll loop.
