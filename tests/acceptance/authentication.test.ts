import { expect, it } from "vitest";
import { createClient } from "@breinstein/oap-client";
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
