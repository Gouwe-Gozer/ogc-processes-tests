# ZOO discovery

Source server: `zoo-local`

This capture contains the landing page, conformance declaration, and complete
process list returned by the local ZOO-Project deployment on 31 August 2026.
The process list advertises 703 processes.

The protocol core should:

- find the conformance, process-list, and job-list resources from the landing
  page links;
- recognize the declared OGC API Processes conformance classes;
- parse the process summaries and preserve their advertised links;
- use each process description to obtain its full input and output schemas.

The stored `Origin` headers represent headers added by a browser. The responses
did not include `Access-Control-Allow-Origin`, so a browser on another origin
cannot read this deployment directly. A relay transport would be required.

The process list is stored exactly as returned by ZOO. It includes every
advertised process, not only the smaller set selected for client scenarios.
