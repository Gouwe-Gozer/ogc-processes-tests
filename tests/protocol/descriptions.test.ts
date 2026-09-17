import { expect, it } from "vitest";
import { parseDescription } from "@breinstein/oap-client";
import { readExchange } from "../support/recorded-fetch.js";

it.each([
  "protocol/execution/pygeoapi-demo/raw-versus-document-response",
  "protocol/discovery/weaver-local/process-description",
])("preserves input and output schemas from %s", async (scenario) => {
  const exchange = await readExchange(scenario, "01-get-description", { baseUrl: "https://processes.test" });
  const { process } = parseDescription(exchange.response.body, { documentUrl: exchange.response.final_url });
  const body = exchange.response.body as {
    id: string;
    inputs: Record<string, { schema: unknown }>;
    outputs: Record<string, { schema: unknown }>;
  };

  expect(process.id).toBe(body.id);
  expect(process.inputs.map((input) => input.id)).toEqual(Object.keys(body.inputs));
  expect(process.outputs.map((output) => output.id)).toEqual(Object.keys(body.outputs));
  for (const input of process.inputs) expect(input.schema).toEqual(body.inputs[input.id]!.schema);
  for (const output of process.outputs) expect(output.schema).toEqual(body.outputs[output.id]!.schema);
});
