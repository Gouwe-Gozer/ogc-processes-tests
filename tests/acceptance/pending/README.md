# Prepared service-authentication workflows

These eight cases are requirements ready for future integration. They are
**not collected tests** because production credential handling is not connected.
The runner announces this gap separately from its client-test results.

[authentication.workflows.ts](authentication.workflows.ts) preserves these
conversations and assertions for both Bearer tokens and API-key headers:

- Configure credentials once; discover, follow pages, submit, poll and read CSV.
- Follow an external result link without leaking the service credential.
- Report wrong credentials and stop discovery.
- Report revoked access during polling without repeating the calculation.

[oap-auth-binding.ts](oap-auth-binding.ts) is the unconnected production binding.
Its guard prevents accidentally running drafts as if credentials were configured.
It must call client-owned credential handling, possibly through the client's
fetch extension. A test-side auth implementation would not test the client.

To activate the cases, connect that binding, move it and the workflow file up
to `tests/acceptance/`, rename the latter to `authentication-workflows.test.ts`,
and adjust its imports. Remove the pending-coverage notice in `vitest.config.ts`
and update coverage notes. Keep the conversations and assertions intact.
TypeScript checks these drafts; Vitest does not collect `.workflows.ts` files.

The two active [explicit-header tests](../authentication.test.ts) exercise
existing public client behaviour. They do not replace these requirements.
