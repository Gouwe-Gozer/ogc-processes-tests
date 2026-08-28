# Postman collections

Generate the collections with:

```bash
python3 scripts/generate_postman_collections.py
```

The command creates:

```text
generated/postman/
├── representative-scenarios.postman_collection.json
└── evidence/
    ├── bgt-prototype.postman_collection.json
    ├── directed-local.postman_collection.json
    ├── pygeoapi-demo.postman_collection.json
    ├── weaver-redoak.postman_collection.json
    └── zoo-local.postman_collection.json
```

## Representative scenarios

The representative collection follows the structure under `scenarios/`. It
contains the small cross-provider set intended for future client tests.

Its recorded `response.json` files become Postman response examples. Matching
`.post-response.js` files are also included. The current asynchronous scripts
save job variables and repeat polling when the collection is run with Postman's
Collection Runner, Postman CLI, or Newman.

## Provider evidence

Each provider gets a separate collection. Its folders are generated from every
request below:

```text
evidence/<provider>/captures/
```

For example, adding future BGT captures under:

```text
evidence/bgt-prototype/captures/discovery/core-discovery/
```

automatically adds `discovery/core-discovery` to the BGT collection. The
generator does not contain a fixed list of providers, operations, processes, or
cases.

Each evidence collection has its own `{{baseUrl}}` collection variable. Its
default comes from that provider's `server.json`. Other placeholders found in
requests, such as `{{jobUrl}}` or `{{resultUrl}}`, are added as empty collection
variables for manual use.

A single-request case becomes one Postman item. A case containing several
requests becomes a folder containing its ordered steps.

Complete matching response files with an inline `body` become Postman response
examples. Large or binary responses that use `body_file` remain in the evidence
folder but are not copied into the collection. This avoids duplicating large
files inside generated JSON.

Evidence collections do not include Postman JavaScript. They are intended for
manual provider inspection. JavaScript copied into Postman by a user is not
written back to these generated files.

Do not edit the generated JSON files. Change a scenario, provider capture,
`server.json`, or the generator and run the command again.
