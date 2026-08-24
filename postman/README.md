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

To reproduce a case in Postman, create this request:

```text
POST {{baseUrl}}/processes/{process_id}/execution
Content-Type: application/json
Body: contents of request.json
```

Import `ogc-processes-tests.postman_collection.json` for basic discovery and
the `hellojs` execution request. The collection variable defaults to
`http://localhost/ogc-api`. Canonical execution cases should remain the
reviewed source of request bodies.
