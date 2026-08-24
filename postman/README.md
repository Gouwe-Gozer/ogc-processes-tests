# Postman

Postman is an optional interface, not the source of truth:

```text
canonical case
(case.json + request.json + fixture)
        |
        +-- curl
        +-- run_case.py
        +-- Postman
        +-- future Topic 3 client
```

Generate the collection from the canonical cases:

```bash
python3 scripts/generate_postman_collection.py
```

The generated layout is:

```text
OGC API Processes tests
├── POST_process_sync
│   └── <case folder name>          POST execution requests
└── process_descriptions
    └── <process_id>                GET process descriptions
```

Each ready `cases/<folder>/` directory becomes one POST item named `<folder>`.
The generator copies the exact `request.json` body, derives the execution URL
from `process_id`, and adds `Prefer: respond-async` for async cases. Those async
cases retain their header inside the requested `POST_process_sync` folder.

The `process_descriptions` folder contains one deduplicated GET request for
every process represented by a generated POST. Pending cases without a request
body are reported and skipped from both folders.

The resulting request has this form:

```text
POST {{baseUrl}}/processes/{process_id}/execution
Content-Type: application/json
Body: contents of request.json
```

Import `ogc-processes-tests.postman_collection.json` after generation. The
collection variable defaults to `http://localhost/ogc-api`; override it in
Postman for another server. The generated collection must not be edited as a
second source of truth.
