import { expect, it } from "vitest";
import { createClient } from "@breinstein/oap-client";
import { recordedFetch } from "../support/recorded-fetch.js";
import { reply } from "../acceptance/exchanges.js";

const baseUrl = "https://responses.test/api/";
const requestedUrl = baseUrl + "results/example";

it("the client keeps the requested URL and final response URL distinct", async () => {
  // Constructed redirect metadata; no actual redirect or browser is simulated.
  const finalUrl = "https://downloads.test/example.json";
  const exchange = reply(requestedUrl, { value: 42 }, 200, "GET", { ETag: '"example-v1"' });
  exchange.response.final_url = finalUrl;
  const transport = recordedFetch(exchange);
  const client = createClient({ baseUrl, fetch: transport.fetch });
  const result = await client.send("results/example");

  expect(result.requestedUrl).toBe(requestedUrl);
  expect(result.url).toBe(finalUrl);
  expect(result.status).toBe(200);
  expect(result.headers.get("etag")).toBe('"example-v1"');
  expect(await result.json()).toEqual({ value: 42 });
  transport.assertDone();
});

it("a second client request returns the new response without replacing the first readable result", async () => {
  const transport = recordedFetch(
    reply(requestedUrl, { value: 1 }),
    reply(requestedUrl, { value: 2 }),
  );
  const client = createClient({ baseUrl, fetch: transport.fetch });
  const first = await client.send("results/example");
  expect(await first.json()).toEqual({ value: 1 });

  const second = await client.send("results/example");
  expect(await second.json()).toEqual({ value: 2 });
  expect(await first.json()).toEqual({ value: 1 });
  expect(first).not.toBe(second);
  transport.assertDone();
});
