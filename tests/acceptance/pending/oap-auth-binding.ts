import { createClient, type FetchLike } from "@breinstein/oap-client";

/**
 * This is the ONLY unfinished connection to OAP in these acceptance cases.
 * The headers below describe the service requirement, not proposed ClientOptions.
 *
 * Replace the guard with calls to the client's actual credential configuration
 * when that implementation is available. Keep the service replies and assertions.
 * Do not add headers in the test transport or implement an auth fetch wrapper here:
 * that would test our implementation instead of the client's.
 */
export function authenticatedClient(
  baseUrl: string,
  fetch: FetchLike,
  credential: { header: string; value: string },
): ReturnType<typeof createClient> {
  // Construct the real client, but do not pretend credentials were configured.
  const client = createClient({ baseUrl, fetch });
  throw new Error(
    "AUTH_INTEGRATION_MISSING: " + client.baseUrl.origin + " requires " + credential.header +
    ". Connect OAP's production credential handling in tests/acceptance/pending/oap-auth-binding.ts. " +
    "No authenticated request has been tested; this is an integration gap, not a proved client defect.",
  );
  // When the real configuration is wired above, return this instance.
  // return client;
}
