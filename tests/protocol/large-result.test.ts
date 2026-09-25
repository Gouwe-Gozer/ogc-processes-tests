import { readFile } from "node:fs/promises";
import { expect, it } from "vitest";
import { BodyTooLargeError, execute, type ExecutePayload } from "@breinstein/oap-client";
import { readExchange, recordedFetch } from "../support/recorded-fetch.js";

it("DIRECTED: returns the complete large CSV as a blob while refusing buffered text", async () => {
  // Retain the capture's actual URL, including its Location header. All HTTP
  // goes through recordedFetch; localhost does not need to be running.
  const baseUrl = "http://localhost:5000";
  const exchange = await readExchange(
    "results/downloads/directed-local/large-raw-csv", "02-execute", { baseUrl },
  );
  const transport = recordedFetch(exchange);
  const result = await execute(`${baseUrl}/processes`, "climada-simple-example-denmark-process", {
    ...exchange.request.body as ExecutePayload,
    fetch: transport.fetch,
  });

  transport.assertDone(); // No polling, even though the CSV response has Location.
  const init = transport.calls[0]![1]!;
  expect(JSON.parse(String(init.body))).toEqual(exchange.request.body);
  expect(new Headers(init.headers).get("content-type")).toBe("application/json");
  // The recorded request used application/json; the client accepts raw results too.
  expect(new Headers(init.headers).get("accept")).toBe("*/*");
  expect(result.kind).toBe("immediate");
  if (result.kind !== "immediate") throw new Error("Expected an immediate CSV result");
  const response = result.response;
  expect(response.status).toBe(200);
  expect(response.requestedUrl).toBe(exchange.request.url);
  expect(response.url).toBe(exchange.response.final_url);
  expect(response.mediaType).toBe("text/csv");
  expect(response.isJson).toBe(false);
  expect(response.location).toBe(exchange.response.headers.Location);
  expect(response.headers.get("content-length")).toBe("18849968");

  // This real payload exceeds the client's default buffer limit. It must remain
  // obtainable as a blob after a caller tries the disallowed text reader.
  expect(response.bodyTooLarge).toBe(true);
  await expect(response.text()).rejects.toBeInstanceOf(BodyTooLargeError);
  const download = await response.blob();
  expect(download.type).toBe("text/csv");
  expect(download.size).toBe(18_849_968);
  const original = await readFile(new URL(exchange.response.body_file!, exchange.responseFile));
  expect(Buffer.from(await download.arrayBuffer()).equals(original), "All recorded CSV bytes are preserved").toBe(true);
});
