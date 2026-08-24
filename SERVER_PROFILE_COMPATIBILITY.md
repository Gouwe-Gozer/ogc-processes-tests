# Server profiles and compatibility scope

## Why this matters

This project tests an OGC API - Processes client, not an Ubuntu client and not
a SAGA-specific client. Nevertheless, the process catalogue exposed by a ZOO-
Project server is influenced by its operating system, ZOO build, processing
engines, optional modules and generated process metadata.

The client should therefore be described as **validated against named server
profiles**, not simply as "compatible with ZOO-Project" or "compatible with OGC
API - Processes".

For the current development phase, the primary profile is:

```text
profile_id: zoo-ubuntu18-gdal3-saga7-otb7
operating_system: Ubuntu 18.04.6 LTS
gdal: 3.0.4
saga: 7.3.0
otb: 7.x (ZOO is configured for OTB 7.0)
```

This is a reproducible interoperability profile and a useful regression target.
It must not silently become the definition of what the final client supports.
Before delivery, the product documentation must state exactly which versions
of ZOO-Project, GDAL, SAGA and OTB have been tested, and distinguish "tested"
from "expected to work".

## The operating system is indirect

The client never communicates with Ubuntu. It communicates with HTTP resources
such as:

```text
/conformance
/processes
/processes/{processID}
/processes/{processID}/execution
/jobs/{jobID}
/jobs/{jobID}/results
```

Ubuntu matters indirectly because its packages and ABI determine which ZOO
providers, GDAL drivers, SAGA tool libraries and OTB applications can be built
and loaded. Upgrading the base image can therefore change the API catalogue and
runtime behaviour even when the client-facing URL remains unchanged.

## How likely are dependency upgrades to break client calls?

The risk depends on the component and on whether the client discovers process
contracts dynamically.

| Component change | Risk to process descriptions and saved calls | Typical changes |
|---|---:|---|
| ZOO-Project upgrade | High | JSON encoding, schema generation, links, error responses, job behaviour, supported execution modes and bug fixes |
| SAGA major/minor upgrade | High | Tool libraries or tool IDs added, removed or reordered; parameter identifiers, types, cardinalities, choices, defaults and outputs changed |
| OTB major/minor upgrade | High | Applications or modules added/removed; dotted parameter keys, mandatory flags, choice values, defaults, input lists and conditional outputs changed |
| GDAL major upgrade | Medium to high | Utility options, defaults, drivers, data types, CRS behaviour and compiled provider compatibility changed |
| GDAL minor upgrade | Low to medium for common formats; higher for driver-specific calls | New or removed drivers, build-dependent format support, changed defaults and edge-case behaviour |
| Different GDAL build with the same version | Medium | Optional drivers and their supported formats depend on build options and external libraries |
| PROJ or CRS database update | Medium | Axis-order handling, available transformations, grid availability and numerical results can change |
| GEOS update | Low for request shape; medium for results | Validity rules, topology fixes and exact output geometries can change |
| MapServer update | Low to medium | Published-reference URLs, supported output services and rendering behaviour can change |
| Python, JavaScript or R runtime update | Low for metadata; medium to high for provider execution | Provider import/loading failures and language-library incompatibilities |
| Base operating-system upgrade | Medium to high indirectly | Package availability, shared-library ABI, locale, TLS and default configuration changes |

### SAGA: high contract-change risk

ZOO generates SAGA process descriptions from the SAGA tool libraries installed
in the image. SAGA itself publishes separately generated tool documentation for
many individual releases. This is strong evidence that the available tools and
their metadata are version-specific.

A SAGA update can change:

- the process ID derived from a library and numeric tool identifier;
- whether a process exists at all;
- an input or output identifier;
- whether an input is optional or repeated;
- literal type, enum values, ranges and defaults;
- the number and media type of outputs;
- algorithm results even when the request remains valid.

Saved calls containing IDs such as `SAGA.grid_tools.27` are consequently
profile-specific. A numeric tool ID must not be assumed to identify the same
contract across SAGA versions.

### OTB: high contract-change risk

OTB applications expose their interfaces from application parameter metadata.
Parameter keys, types, choices, mandatory state and defaults are part of each
application implementation. ZOO uses that metadata to create its OGC process
descriptions.

OTB 9 and later also support independently installable modules. Two images with
the same OTB version can therefore expose different application catalogues when
different modules are installed.

Saved OTB requests are particularly sensitive to:

- dotted parameter keys such as `mode.vector.out`;
- conditional parameters enabled by another choice;
- input image and vector-data lists;
- renamed choice values or changed defaults;
- applications moving into optional modules;
- raster versus vector output modes.

### GDAL: more stable core, but not a fixed contract

Common formats and core GDAL/OGR concepts are relatively stable, so calls using
GeoJSON, GML, GeoTIFF and simple geometry operations are less likely to change
than generated SAGA or OTB calls.

The risk is still material:

- GDAL's migration guidance records changed defaults, data types, command
  interfaces, SQL behaviour and removed or disabled drivers;
- driver availability depends on how GDAL was compiled and which external
  libraries were available;
- a media type advertised by one build might not be writable by another build;
- ZOO's compiled GDAL provider libraries must match the runtime GDAL ABI;
- algorithm results and error messages can change without changing the request
  schema.

The new unified `gdal` command introduced in later GDAL versions is explicitly
described upstream as provisional. Our tests should prefer the process contract
advertised by ZOO rather than assuming long-term command-line compatibility.

## What should and should not break the client

An update may legitimately invalidate a saved **process-specific request**. It
should not crash or fundamentally break a well-designed generic client.

The client should expect that a server upgrade can:

- add, remove or rename processes;
- change a process version;
- add or remove inputs and outputs;
- change `minOccurs`, `maxOccurs`, enums, ranges or defaults;
- change supported media types and encodings;
- change whether inline values or references are accepted;
- change job-control and output-transmission capabilities;
- return a previously unseen but valid JSON Schema fragment;
- return a valid OGC problem response for an execution that used to succeed;
- expose malformed metadata or a broken process link as a server defect.

The generic client should therefore:

1. Fetch `/conformance` and process descriptions from the actual target server.
2. Treat the process description as the contract for that server profile.
3. Avoid hard-coding SAGA or OTB parameter sets into generic client logic.
4. Support arrays, bounding boxes, inline qualified values, links, `oneOf`,
   enums, defaults, nullable values and multiple outputs.
5. Use declared media types rather than guessing from file extensions.
6. Tolerate unknown metadata fields and unsupported schema constructs without
   crashing.
7. Report that a saved call no longer matches the current process description
   instead of blindly submitting it.
8. Cache descriptions only with a profile/version/hash and provide a way to
   refresh them.

Tests that assert exact numerical or geometric outputs should use tolerances or
semantic comparisons where appropriate. A topology or interpolation bug fix can
change a correct result without changing the HTTP contract.

## Separate protocol tests from provider-profile tests

The test suite should have two layers.

### Protocol-level tests

These should remain portable across server profiles and exercise:

- discovery and conformance;
- process-description parsing;
- literal, bounding-box, inline and reference inputs;
- arrays and multiple outputs;
- synchronous and asynchronous execution;
- job status, dismissal and result retrieval;
- error and problem-detail handling.

They should use deliberately simple processes whose contracts we control where
possible.

### Provider-profile tests

These are tied to an explicit engine version and include calls such as:

```text
SAGA.grid_tools.0
SAGA.grid_tools.27
OTB.Segmentation
Gdal_Warp
```

Their evidence, expected request and expected response must state the server
profile against which they were captured.

## Required profile record

For every supported deployment profile, record at least:

```yaml
profile_id: zoo-ubuntu18-gdal3-saga7-otb7
captured_at: 2026-08-24
image_reference: zoo-project:local
image_digest: TODO
operating_system: Ubuntu 18.04.6 LTS
zoo_project_commit: TODO
zoo_project_version: TODO
gdal_version: 3.0.4
proj_version: TODO
geos_version: TODO
saga_version: 7.3.0
otb_version: 7.x
mapserver_version: TODO
python_version: 3.6.x
r_version: 3.6.3
process_collection_sha256: TODO
```

The image digest and process-collection hash are important. A mutable image tag
such as `latest` is not sufficient evidence that two test runs used the same
server contract.

## Upgrade qualification workflow

Do not replace the current profile in place when evaluating a newer stack.

1. Build the new stack under a new profile ID, for example
   `zoo-ubuntu24-gdal3-saga9-otb9`.
2. Capture `/conformance`, `/processes` and every selected detailed process
   description.
3. Compare process IDs and normalized input/output schemas with the previous
   profile.
4. Classify changes as compatible additions, intentional breaking changes or
   server regressions.
5. Run the protocol-level suite against both profiles.
6. Run provider-specific calls only where that profile advertises a matching
   contract.
7. Promote the new profile to primary only after documenting the results.

The final product should ideally be validated against at least one maintained,
modern profile in addition to the frozen Ubuntu 18.04 regression profile.

## Official references

- [OGC API - Processes - Part 1: Core](https://docs.ogc.org/is/18-062r2/18-062r2.html)
  defines process descriptions using JSON Schema fragments and makes those
  descriptions the contract for execute-request inputs and outputs.
- [SAGA tool-library documentation](https://saga-gis.sourceforge.io/saga_tool_doc/index.html)
  publishes version-specific, automatically generated tool metadata.
- [OTB command-line interface](https://www.orfeo-toolbox.org/CookBook/CliInterface.html)
  documents application names and generated parameter interfaces.
- [OTB modules](https://www.orfeo-toolbox.org/CookBook-develop/Modules.html)
  documents the modular packaging introduced with OTB 9.
- [GDAL migration guide](https://gdal.org/en/stable/user/migration_guide.html)
  records behavioural, API, utility and driver changes between releases.
- [Building GDAL from source](https://gdal.org/en/stable/development/building_from_source.html)
  documents build-dependent optional raster and vector drivers.
- [GDAL programs](https://gdal.org/en/stable/programs/index.html) notes that the
  newer unified `gdal` command does not yet promise backward compatibility.
