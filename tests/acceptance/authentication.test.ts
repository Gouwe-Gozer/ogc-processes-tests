import { expect, it } from "vitest";
import { createClient, execute, ProcessesError } from "@breinstein/oap-client";
import { protectedConversation } from "./protected-conversation.js";
import { reply } from "./exchanges.js";

const base = "https://protected.test/api/";
const origin = new URL(base).origin;
const catalogue = base + "processes";

// OpenAPI permits a service to choose its API-key header name. This example
// deliberately does not depend on the commonly used X-API-Key spelling.
const credentials = [
  { name: "Bearer", header: "Authorization", value: "Bearer public-test-token", status: 401,
    challenge: 'Bearer realm="acceptance"' },
  { name: "API key", header: "X-Processing-Key", value: "public-test-api-key", status: 403 },
];

it.each(credentials)("$name: the client sends explicit credentials and preserves service refusals", async (credential) => {
  const transport = protectedConversation(origin, credential,
    reply(catalogue, { processes: [], links: [{ rel: "self", href: catalogue }] }),
  );
  const client = createClient({ baseUrl: base, fetch: transport.fetch });
  const missing = await client.send(catalogue);
  const wrongValue = credential.name === "Bearer" ? "Bearer wrong" : "wrong";
  const wrong = await client.send(catalogue, { headers: { [credential.header]: wrongValue } });
  const accepted = await client.send(catalogue, { headers: { [credential.header]: credential.value } });
  expect(missing.status).toBe(credential.status);
  expect(wrong.status).toBe(credential.status);
  expect(await wrong.json()).toMatchObject({ status: credential.status, title: "Access denied" });
  if (credential.challenge) expect(missing.headers.get("www-authenticate")).toBe(credential.challenge);
  expect(accepted.status).toBe(200);
  expect(await accepted.json()).toMatchObject({ processes: [] });
  expect(transport.calls.map(([url]) => url)).toEqual([catalogue, catalogue, catalogue]);
  expect(transport.calls.map(([, init]) => new Headers(init?.headers).get(credential.header)))
    .toEqual([null, wrongValue, credential.value]);
  if (credential.challenge) expect(wrong.headers.get("www-authenticate"))
    .toBe(credential.challenge + ', error="invalid_token"');
  transport.assertDone();
});

// The service requires a credential, but none is supplied. These are real core
// operations, not a placeholder for a future auth configuration API. The gate
// rejects the client's actual requests; no test helper adds or refreshes a key.
for (const credential of credentials) {
  async function expectAccessDenied(operation: Promise<unknown>) {
    const error: unknown = await operation.catch((cause: unknown) => cause);
    expect(error).toBeInstanceOf(ProcessesError);
    if (!(error instanceof ProcessesError)) throw new Error("Expected the service's access refusal");
    expect(error.status).toBe(credential.status);
    expect(error.problem).toMatchObject({
      title: "Access denied", status: credential.status,
      detail: "Supply the configured service credential.",
    });
    expect(error.envelope.mediaType).toBe("application/problem+json");
    expect(error.envelope.headers.get("www-authenticate")).toBe(credential.challenge ?? null);
    return error;
  }

  it(`${credential.name}: protected discovery reports the refusal without trying a guessed catalogue`, async () => {
    const transport = protectedConversation(origin, credential);
    const client = createClient({ baseUrl: base, fetch: transport.fetch });
    await expectAccessDenied(client.listProcesses());
    expect(transport.calls.map(([url]) => url),
      "After an authentication refusal, stop and let the caller supply credentials; do not try another endpoint",
    ).toEqual([base]);
    transport.assertDone();
  });

  it(`${credential.name}: protected execution reports the refusal without repeating the POST`, async () => {
    const transport = protectedConversation(origin, credential);
    const executionUrl = catalogue + "/example/execution";
    const inputs = { day: "2026-09-15" };
    // Public core entry point for an already-known process collection. This
    // isolates submission from discovery so both behaviours are tested.
    const error = await expectAccessDenied(execute(catalogue, "example", {
      inputs, mode: "async", fetch: transport.fetch,
    }));
    expect(error.url).toBe(executionUrl);
    expect(transport.calls.map(([url, init]) => [url, init?.method])).toEqual([[executionUrl, "POST"]]);
    expect(JSON.parse(String(transport.calls[0]![1]?.body)).inputs).toEqual(inputs);
    transport.assertDone();
  });

  it(`${credential.name}: protected polling reports the refusal and stops without resubmitting`, async () => {
    const transport = protectedConversation(origin, credential);
    const client = createClient({ baseUrl: base, fetch: transport.fetch });
    const jobUrl = base + "jobs/example";
    const observed: string[] = [];
    const error = await expectAccessDenied(client.pollJob(jobUrl, {
      intervalMs: 500, maxPolls: 3, timeoutMs: 10_000,
      onStatus: (status) => observed.push(status.status),
    }));
    expect(error.url).toBe(jobUrl);
    expect(observed).toEqual([]);
    expect(transport.calls.map(([url, init]) => [url, init?.method])).toEqual([[jobUrl, "GET"]]);
    transport.assertDone();
  });

  it(`${credential.name}: protected results report the refusal instead of returning it as a download`, async () => {
    const transport = protectedConversation(origin, credential);
    const client = createClient({ baseUrl: base, fetch: transport.fetch });
    const jobUrl = base + "jobs/example";
    const resultUrl = base + "outputs/example.csv";
    const error = await expectAccessDenied(client.getResults(jobUrl, {
      links: [{ rel: "http://www.opengis.net/def/rel/ogc/1.0/results", href: resultUrl, type: "text/csv" }],
    }));
    expect(error.url).toBe(resultUrl);
    expect(transport.calls.map(([url, init]) => [url, init?.method])).toEqual([[resultUrl, "GET"]]);
    transport.assertDone();
  });
}
