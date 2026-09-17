import { expect, it } from "vitest";
import { readExchange, recordedFetch } from "./recorded-fetch.js";

const scenario = "protocol/execution/zoo-local/simple-sync";
const baseUrl = "https://zoo.test";

it("fails when a capture placeholder has no explicit value", async () => {
  await expect(readExchange(scenario, "01-execute")).rejects.toThrow("Unresolved fixture variable baseUrl");
});

it("does not let caught request mismatches or extra requests appear complete", async () => {
  const exchange = await readExchange(scenario, "01-execute", { baseUrl });
  const transport = recordedFetch(exchange);
  await expect(transport.fetch(exchange.request.url, { method: "GET" })).rejects.toThrow("Request method differs");
  await transport.fetch(exchange.request.url, { method: "POST" });
  expect(() => transport.assertDone()).toThrow("Unexpected or missing recorded requests");
  await expect(transport.fetch(exchange.request.url, { method: "POST" })).rejects.toThrow("Unexpected request");
});

it("rejects a wrong URL and detects an unused recording", async () => {
  const exchange = await readExchange(scenario, "01-execute", { baseUrl });
  const transport = recordedFetch(exchange);
  await expect(transport.fetch(`${baseUrl}/wrong`, { method: "POST" })).rejects.toThrow("Request URL differs");
  expect(() => transport.assertDone()).toThrow("Not every recorded exchange was consumed");
  expect(() => recordedFetch(exchange).assertDone()).toThrow("Unexpected or missing recorded requests");
});

it("returns fresh bodies and preserves a final URL separately from the requested URL", async () => {
  const exchange = await readExchange(scenario, "01-execute", { baseUrl });
  // A controlled loader check, not a new claim about the recorded provider.
  const redirected = { ...exchange, response: { ...exchange.response, final_url: "https://final.test/result" } };
  const transport = recordedFetch(redirected, redirected);
  const first = await transport.fetch(exchange.request.url, { method: "POST" });
  expect(first.url).toBe("https://final.test/result");
  expect(first.headers.get("content-type")).toBe(exchange.response.headers["Content-Type"]);
  expect(await first.json()).toEqual(exchange.response.body);
  const second = await transport.fetch(exchange.request.url, { method: "POST" });
  expect(await second.json()).toEqual(exchange.response.body);
  transport.assertDone();
});

it("reads body_file relative to the response capture and returns the original CSV bytes", async () => {
  const exchange = await readExchange(
    "results/downloads/directed-local/large-raw-csv", "02-execute", { baseUrl },
  );
  const transport = recordedFetch(exchange);
  const response = await transport.fetch(exchange.request.url, { method: exchange.request.method });
  const bytes = await response.arrayBuffer();
  expect(bytes.byteLength).toBe(18_849_968);
  expect(response.headers.get("content-type")).toBe("text/csv");
  expect(new TextDecoder().decode(bytes.slice(0, 100))).toContain(",");
  transport.assertDone();
});
