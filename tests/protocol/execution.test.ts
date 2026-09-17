import { describe, expect, it } from "vitest";
import { execute, parseDescription, type ExecutePayload } from "@breinstein/oap-client";
import { readExchange, recordedFetch } from "../support/recorded-fetch.js";

it("ZOO: sends the recorded inputs and preserves the immediate result", async () => {
  const baseUrl = "https://zoo.test/ogc-api";
  const exchange = await readExchange("protocol/execution/zoo-local/simple-sync", "01-execute", { baseUrl });
  const transport = recordedFetch(exchange);
  const result = await execute(`${baseUrl}/processes`, "hellojs", {
    ...exchange.request.body as ExecutePayload,
    fetch: transport.fetch,
  });

  transport.assertDone();
  const init = transport.calls[0]![1]!;
  expect(JSON.parse(String(init.body))).toEqual(exchange.request.body);
  expect(new Headers(init.headers).get("content-type")).toBe("application/json");
  // The capture used application/json; this client's execute API deliberately uses */*.
  expect(new Headers(init.headers).get("accept")).toBe("*/*");
  expect(new Headers(init.headers).has("prefer")).toBe(false);
  expect(result.kind).toBe("immediate");
  if (result.kind !== "immediate") throw new Error("Expected an immediate result");
  expect(result.requestedMode).toBe("sync");
  expect(result.response.status).toBe(200);
  expect(result.response.requestedUrl).toBe(exchange.request.url);
  expect(result.response.url).toBe(exchange.response.final_url);
  expect(await result.response.json()).toEqual(exchange.response.body);
});

describe("pygeoapi: advertised execution link and both response modes", () => {
  it.each(["02-execute-default-raw", "03-execute-document"])("%s", async (step) => {
    // Keep absolute advertised links intact; every request still goes to recordedFetch.
    const baseUrl = "https://demo.pygeoapi.io/stable";
    const scenario = "protocol/execution/pygeoapi-demo/raw-versus-document-response";
    const description = await readExchange(scenario, "01-get-description", { baseUrl });
    const exchange = await readExchange(scenario, step, { baseUrl });
    const parsed = parseDescription(description.response.body, { documentUrl: description.response.final_url });
    const transport = recordedFetch(exchange);
    const result = await execute(`${baseUrl}/processes`, parsed.process.id, {
      ...exchange.request.body as ExecutePayload,
      description: parsed.process,
      fetch: transport.fetch,
    });

    transport.assertDone();
    expect(transport.calls[0]![0]).toBe(`${baseUrl}/processes/hello-world/execution?f=json`);
    expect(JSON.parse(String(transport.calls[0]![1]!.body))).toEqual(exchange.request.body);
    expect(parsed.process.inputs.find((input) => input.id === "name")?.required).toBe(true);
    expect(result.kind).toBe("immediate");
    if (result.kind !== "immediate") throw new Error("Expected an immediate result");
    expect(result.response.mediaType).toBe("application/json");
    expect(await result.response.json()).toEqual(exchange.response.body);
    // Classification must not consume the only readable copy of the body.
    expect(await result.response.json()).toEqual(exchange.response.body);
  });
});

it("Weaver: preserves an immediate result despite job-related response headers", async () => {
  const baseUrl = "https://weaver.test";
  const syncJobUrl = `${baseUrl}/processes/EchoProcess/jobs/sync-1`;
  const exchange = await readExchange(
    "protocol/execution/weaver-local/sync-with-job-links", "01-execute",
    { baseUrl, syncJobId: "sync-1", syncJobUrl },
  );
  const payload = exchange.request.body as ExecutePayload;
  // The recording also carries body.mode and Prefer: wait=30. The current
  // public execute API expresses sync as an option and sends neither on the wire.
  const options = { inputs: payload.inputs!, response: "document" as const, mode: "sync" as const };
  const transport = recordedFetch(exchange);
  const result = await execute(`${baseUrl}/processes`, "EchoProcess", { ...options, fetch: transport.fetch });

  transport.assertDone();
  const init = transport.calls[0]![1]!;
  expect(JSON.parse(String(init.body))).toEqual({ inputs: payload.inputs, response: "document" });
  expect(new Headers(init.headers).has("prefer")).toBe(false);
  expect(result.kind).toBe("immediate");
  if (result.kind !== "immediate") throw new Error("Expected an immediate result");
  expect(result.response.headers.get("content-location")).toBe(`${syncJobUrl}/results`);
  expect(result.response.links).toEqual(expect.arrayContaining([
    expect.objectContaining({ rel: "monitor", href: syncJobUrl }),
  ]));
  expect(await result.response.json()).toEqual(exchange.response.body);
});
