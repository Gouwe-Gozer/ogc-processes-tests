import { expect, it } from "vitest";
import { createClient } from "@breinstein/oap-client";
import { readExchange, recordedFetch } from "../support/recorded-fetch.js";

it("Weaver: follows discovery links through the injected fetch to list processes", async () => {
  const baseUrl = "https://redoak.cs.toronto.edu/weaver";
  const scenario = "protocol/discovery/weaver-redoak/core-discovery";
  const [landing, conformance, listing] = await Promise.all([
    readExchange(scenario, "01-landing", { baseUrl }),
    readExchange(scenario, "02-conformance", { baseUrl }),
    readExchange(scenario, "03-processes", { baseUrl }),
  ]);
  const transport = recordedFetch(landing, conformance, listing);
  const client = createClient({ baseUrl, fetch: transport.fetch });
  const result = await client.listProcesses();

  transport.assertDone();
  const body = listing.response.body as { processes: { id: string }[] };
  expect(result.processes.map((process) => process.id)).toEqual(body.processes.map((process) => process.id));
  expect(result.pageCount).toBe(1);
  expect(result.truncated).toBe(false);
  for (const [, init] of transport.calls) {
    expect(new Headers(init?.headers).get("accept")).toBe("application/json");
  }
});
