import { expect, it } from "vitest";
import { execute, type ExecutePayload } from "@breinstein/oap-client";
import { readExchange, recordedFetch } from "../support/recorded-fetch.js";

it.each([
  ["zoo-local", "longProcess"],
  ["weaver-local", "EchoProcess"],
])("%s: returns an accepted job without starting to poll", async (provider, processId) => {
  const baseUrl = "https://processes.test";
  const jobId = "recorded-job";
  const jobUrl = `${baseUrl}/jobs/${jobId}`;
  const exchange = await readExchange(
    `protocol/jobs/${provider}/successful-job`, "01-submit", { baseUrl, jobId, jobUrl },
  );
  const payload = exchange.request.body as ExecutePayload;
  const transport = recordedFetch(exchange);
  const result = await execute(`${baseUrl}/processes`, processId, {
    inputs: payload.inputs!, response: "document", mode: "async", fetch: transport.fetch,
  });

  // One response only: a hidden retry or automatic poll fails this check.
  transport.assertDone();
  const init = transport.calls[0]![1]!;
  expect(new Headers(init.headers).get("prefer")).toBe("respond-async");
  // body.mode in the Weaver recording is not a member of the client's payload.
  expect(JSON.parse(String(init.body))).toEqual({ inputs: payload.inputs, response: "document" });
  expect(result.kind).toBe("job");
  if (result.kind !== "job") throw new Error("Expected a job handle");
  expect(result.requestedMode).toBe("async");
  expect(result.job.statusUrl).toBe(jobUrl);
  expect(result.job.jobId).toBe(jobId);
  expect(result.job.discoveredVia).toBe("location-header");
});
