import { expect, it } from "vitest";
import { execute, getProcess, ProcessesError, type ExecutePayload } from "@breinstein/oap-client";
import { readExchange, recordedFetch } from "../support/recorded-fetch.js";

it("ZOO: retains a structured execution refusal as ProcessesError", async () => {
  const baseUrl = "https://zoo.test/ogc-api";
  const exchange = await readExchange(
    "protocol/errors/zoo-local/structured-execution-error", "01-execute", { baseUrl },
  );
  const transport = recordedFetch(exchange);
  const error: unknown = await execute(`${baseUrl}/processes`, "failR", {
    ...exchange.request.body as ExecutePayload,
    fetch: transport.fetch,
  }).catch((cause: unknown) => cause);

  transport.assertDone();
  expect(JSON.parse(String(transport.calls[0]![1]!.body))).toEqual(exchange.request.body);
  expect(error).toBeInstanceOf(ProcessesError);
  if (!(error instanceof ProcessesError)) throw new Error("Expected ProcessesError");
  expect(error.status).toBe(500);
  expect(error.outcome).toBe("exception");
  expect(error.problem).toMatchObject(exchange.response.body as Record<string, unknown>);
  expect(error.url).toBe(exchange.response.final_url);
  expect(await error.envelope.json()).toEqual(exchange.response.body);
});

it("ZOO: retains an HTML description failure as an HTTP error, not a transport failure", async () => {
  const baseUrl = "https://zoo.test/ogc-api";
  const exchange = await readExchange(
    "protocol/errors/zoo-local/process-description-html-error", "01-get-description", { baseUrl },
  );
  const transport = recordedFetch(exchange);
  const error: unknown = await getProcess(`${baseUrl}/processes`, "OTB.ReadImageInfo", {
    fetch: transport.fetch,
  }).catch((cause: unknown) => cause);

  transport.assertDone();
  expect(new Headers(transport.calls[0]![1]!.headers).get("accept")).toBe("application/json");
  expect(error).toBeInstanceOf(ProcessesError);
  if (!(error instanceof ProcessesError)) throw new Error("Expected ProcessesError");
  expect(error.status).toBe(500);
  expect(error.outcome).toBe("http-error");
  expect(error.problem).toBeUndefined();
  expect(error.bodyPreview).toContain("500 Internal Server Error");
  expect(await error.envelope.text()).toBe(exchange.response.body);
});
