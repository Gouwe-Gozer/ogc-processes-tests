import { expect, it } from "vitest";
import {
  dismissJob, execute, getResults, pollJob, ProcessesError, waitForJob,
  type ExecutePayload, type JobStatus,
} from "@breinstein/oap-client";
import { readExchange, recordedFetch } from "../support/recorded-fetch.js";

const baseUrl = "https://processes.test";
const jobId = "recorded-job";
const jobUrl = `${baseUrl}/jobs/${jobId}`;
const variables = {
  baseUrl, jobId, jobUrl, resultsUrl: `${jobUrl}/results`,
  complexObjectUrl: `${jobUrl}/files/object.json`,
  geometryUrl: `${jobUrl}/files/point.geojson`,
  secondGeometryUrl: `${jobUrl}/files/polygon.json`,
  imageUrl: `${jobUrl}/files/image.tif`,
  featureCollectionUrl: `${jobUrl}/files/features.geojson`,
};

it.each([
  { provider: "zoo-local", processId: "longProcess", polls: ["02-poll.running", "02-poll.successful"] },
  // Weaver only has a successful status capture. Do not invent an intermediate reply.
  { provider: "weaver-local", processId: "EchoProcess", polls: ["02-poll.successful"] },
])("$provider: submits, polls to success and follows the advertised results link", async ({ provider, processId, polls }) => {
  const scenario = `protocol/jobs/${provider}/successful-job`;
  const submission = await readExchange(scenario, "01-submit", variables);
  const statuses = await Promise.all(polls.map((step) => readExchange(scenario, "02-poll", variables, step)));
  const results = await readExchange(scenario, "03-results", variables);
  const transport = recordedFetch(submission, ...statuses, results);
  const payload = submission.request.body as ExecutePayload;
  const execution = await execute(`${baseUrl}/processes`, processId, {
    inputs: payload.inputs!, response: "document", mode: "async", fetch: transport.fetch,
  });
  expect(execution.kind).toBe("job");
  if (execution.kind !== "job") throw new Error("Expected a job handle");
  expect(execution.job.statusUrl).toBe(jobUrl);

  const observed: JobStatus[] = [];
  // Use the public polling loop and a short real interval, not a replacement clock
  // or loop. This checks recorded states, not the client's backoff algorithm.
  const report = await pollJob(execution.job.statusUrl, {
    fetch: transport.fetch, intervalMs: 500, timeoutMs: 10_000, maxPolls: statuses.length + 1,
    onStatus: (status) => observed.push(status),
  });
  expect(report.outcome).toBe("terminal");
  expect(report.pollCount).toBe(statuses.length);
  const expectedStates = statuses.map((exchange) => (exchange.response.body as { status: string }).status);
  expect(report.statusSequence).toEqual(expectedStates);
  expect(observed.map((status) => status.status)).toEqual(expectedStates);
  if (provider === "zoo-local") {
    expect(observed[0]).toMatchObject({ status: "running", terminal: false, progress: 80, message: "Step 80" });
  }
  const status = report.status;
  expect(status).toMatchObject({ jobId, status: "successful", terminal: true });
  if (!status) throw new Error("Expected a final status");

  const result = await getResults(execution.job.statusUrl, { status, fetch: transport.fetch });
  transport.assertDone();
  expect(result.route).toBe("advertised-link");
  expect(result.url).toBe(results.request.url);
  expect(result.envelope.status).toBe(200);
  expect(result.envelope.url).toBe(results.response.final_url);
  expect(await result.envelope.json()).toEqual(results.response.body);
  // Output hrefs remain values in the result document; no file is fetched here.
  expect(await result.envelope.json()).toEqual(results.response.body);
  for (const [, init] of transport.calls.slice(1, -1)) {
    expect(new Headers(init?.headers).get("accept")).toBe("application/json");
  }
  expect(new Headers(transport.calls.at(-1)![1]?.headers).get("accept")).toBe("application/json, */*;q=0.8");
});

it("ZOO: a failed job resolves with the recorded explanation and does not fetch results", async () => {
  const exchange = await readExchange("protocol/jobs/zoo-local/failed-job", "02-poll-failed", variables);
  const transport = recordedFetch(exchange);
  const status = await waitForJob(jobUrl, { fetch: transport.fetch, maxPolls: 2 });

  transport.assertDone();
  expect(status).toMatchObject({ jobId, status: "failed", terminal: true });
  expect(status.message).toBe((exchange.response.body as { message: string }).message);
  expect(status.exception).toBeUndefined();
});

it("Weaver: results requested too early retain the result-not-ready problem", async () => {
  const exchange = await readExchange("protocol/jobs/weaver-local/results-not-ready", "02-results", variables);
  const transport = recordedFetch(exchange);
  const error: unknown = await getResults(jobUrl, { fetch: transport.fetch }).catch((cause: unknown) => cause);

  transport.assertDone();
  expect(error).toBeInstanceOf(ProcessesError);
  if (!(error instanceof ProcessesError)) throw new Error("Expected ProcessesError");
  expect(error.status).toBe(404);
  expect(error.outcome).toBe("exception");
  expect(error.problem).toMatchObject({
    title: "JobResultsNotReady",
    type: "https://www.opengis.net/def/exceptions/ogcapi-processes-1/1.0/result-not-ready",
  });
  expect(await error.envelope.json()).toEqual(exchange.response.body);
});

it("ZOO: dismisses a submitted job and preserves the returned dismissed status", async () => {
  const scenario = "protocol/jobs/zoo-local/dismiss-running-job";
  const submission = await readExchange(scenario, "01-submit", variables);
  const dismissal = await readExchange(scenario, "02-dismiss", variables);
  const transport = recordedFetch(submission, dismissal);
  const payload = submission.request.body as ExecutePayload;
  const execution = await execute(`${baseUrl}/processes`, "longProcess", {
    inputs: payload.inputs!, response: "document", mode: "async", fetch: transport.fetch,
  });
  if (execution.kind !== "job") throw new Error("Expected a job handle");
  const result = await dismissJob(execution.job.statusUrl, { fetch: transport.fetch });

  transport.assertDone();
  expect(result.kind).toBe("dismissed");
  if (result.kind !== "dismissed") throw new Error("Expected dismissal");
  expect(result.status).toMatchObject({ jobId, status: "dismissed", terminal: true });
  expect(await result.envelope.json()).toEqual(dismissal.response.body);
});
