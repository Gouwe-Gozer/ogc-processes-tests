# Supporting evidence

This folder keeps provider-specific material that may help explain client or
server behaviour but is not part of the small representative set in
[`../scenarios/`](../scenarios/).

The three server folders contain server details and captured material:

- [`zoo-local/`](zoo-local/): 53 runnable requests plus captured process
  descriptions, execution responses, errors, and diagnostics;
- [`pygeoapi-demo/`](pygeoapi-demo/): details of the public pygeoapi demo used
  for the recorded `hello-world` exchanges;
- [`bgt-prototype/`](bgt-prototype/): details of the local pygeoapi-based BGT
  prototype.

[`recorded-exchanges/`](recorded-exchanges/) contains complete request and
response pairs that are not in the main scenario set. These include similar
processes, provider-specific failures, validation observations, and unusual
responses. Their README files explain why each exchange was kept.

Names such as `Handling` and `Expected client handling` in those notes are
plain-language classifications. They do not define a required client API,
testcase format, or provider-specific adapter.

Each file below `zoo-local/requests/` contains one complete runnable request:
method, path, headers, body, expected status, and supporting notes. Run one with
[`../scripts/run_evidence_request.py`](../scripts/run_evidence_request.py).
