# Implementation interoperability samples

This directory contains deliberately small, recorded fixtures from additional
OGC API Processes implementations and deployments. They demonstrate that the
client core is not coupled to the selected ZOO profile; they are not provider
or implementation conformance suites.

The checked-in responses are the stable test inputs. A live service is useful
for occasional smoke testing, but is not required for normal client tests.

## Implementations and deployments

- [`pygeoapi/`](pygeoapi/) compares the official stable demo with a custom
  local deployment. Processor metadata and results are application behaviour,
  even when pygeoapi supplies the surrounding HTTP API.

Deployment-specific URL variables are intentional. Request descriptors must
not assume that all samples are hosted below `{{baseUrl}}`.

[`suite.json`](suite.json) records the template variable and default URL for
each deployment so future runners and collection generators do not need to
hard-code provider names.
