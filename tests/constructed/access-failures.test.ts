import { expect, it } from "vitest";
import { createClient, ProcessesError, type JobStatus } from "@breinstein/oap-client";
import { recordedFetch, type readExchange } from "../support/recorded-fetch.js";

// Constructed access refusals. No credentials are created, checked or refreshed.
const baseUrl = "https://access.test/api/";
const processesUrl = `${baseUrl}processes`;
const firstPageUrl = `${processesUrl}?limit=1`;
const secondPageUrl = `${processesUrl}?cursor=second`;
const processId = "access-example";
const executionUrl = `${processesUrl}/${processId}/execution`;
const statusUrl = `${baseUrl}jobs/example`;
const resultsUrl = `${baseUrl}outputs/example/result.json`;
const payload = { inputs: { message: "Access check" }, response: "document" as const };

function reply(
  url: string, body: Record<string, unknown>, status = 200, method = "GET",
  headers: Record<string, string> = {},
) {
  return {
    request: { url, method, headers: {} },
    response: { status, headers: { "Content-Type": "application/json", ...headers }, final_url: url, body },
    // Inline responses only; the existing transport uses this base for body_file.
    responseFile: new URL(import.meta.url),
  } satisfies Awaited<ReturnType<typeof readExchange>>;
}

function discovery() {
  return [
    reply(baseUrl, {
      title: "Constructed access-failure service",
      links: [
        { rel: "conformance", href: "conformance", type: "application/json" },
        { rel: "http://www.opengis.net/def/rel/ogc/1.0/processes", href: "processes", type: "application/json" },
      ],
    }),
    reply(`${baseUrl}conformance`, {
      conformsTo: ["http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/core"],
    }),
  ];
}

function acceptedSubmission() {
  return reply(executionUrl, {
    jobID: "example", processID: processId, type: "process", status: "accepted",
    links: [{ rel: "monitor", href: statusUrl, type: "application/json" }],
  }, 201, "POST", { Location: statusUrl });
}

async function expectRefusal(operation: Promise<unknown>, refusal: ReturnType<typeof reply>) {
  const error: unknown = await operation.catch((cause: unknown) => cause);
  expect(error).toBeInstanceOf(ProcessesError);
  if (!(error instanceof ProcessesError)) throw new Error("Expected an HTTP access refusal");
  expect(error.status).toBe(refusal.response.status);
  expect(error.url).toBe(refusal.response.final_url);
  expect(error.outcome).toBe("exception");
  expect(error.problem).toMatchObject(refusal.response.body);
  expect(error.envelope.mediaType).toBe("application/problem+json");
  expect(await error.envelope.json()).toEqual(refusal.response.body);
  return error;
}

function expectOneSubmission(transport: ReturnType<typeof recordedFetch>) {
  const submissions = transport.calls.filter(([, init]) => init?.method === "POST");
  expect(submissions).toHaveLength(1);
  expect(submissions[0]?.[0]).toBe(executionUrl);
  expect(JSON.parse(String(submissions[0]?.[1]?.body))).toEqual(payload);
}

it("constructed: a catalogue page returning 401 rejects listing and retains its authentication challenge", async () => {
  const challenge = 'Bearer realm="constructed-service"';
  const refusal = reply(secondPageUrl, {
    type: "about:blank", title: "Unauthorized", status: 401,
    detail: "Access to this catalogue page requires credentials.",
  }, 401, "GET", { "Content-Type": "application/problem+json", "WWW-Authenticate": challenge });
  const transport = recordedFetch(
    ...discovery(),
    reply(firstPageUrl, {
      processes: [{ id: processId, version: "1.0.0", jobControlOptions: ["async-execute"] }],
      numberTotal: 2,
      links: [{ rel: "next", href: "?cursor=second", type: "application/json" }],
    }),
    refusal,
  );
  const client = createClient({ baseUrl, fetch: transport.fetch });
  const error = await expectRefusal(client.listProcesses({ limit: 1 }), refusal);

  expect(error.envelope.headers.get("www-authenticate")).toBe(challenge);
  transport.assertDone(); // No retry, fallback catalogue or execution after this refusal.
  expect(transport.calls.map(([url]) => url)).toEqual([
    baseUrl, `${baseUrl}conformance`, firstPageUrl, secondPageUrl,
  ]);
});

it("constructed: execution returning 403 rejects without repeating the POST or starting polling", async () => {
  const refusal = reply(executionUrl, {
    type: "about:blank", title: "Forbidden", status: 403,
    detail: "You do not have permission to execute this process.",
  }, 403, "POST", { "Content-Type": "application/problem+json" });
  const transport = recordedFetch(...discovery(), refusal);
  const client = createClient({ baseUrl, fetch: transport.fetch });
  await expectRefusal(client.execute(processId, { ...payload, mode: "async" }), refusal);

  transport.assertDone();
  expectOneSubmission(transport);
  expect(transport.calls.map(([url]) => url)).toEqual([
    baseUrl, `${baseUrl}conformance`, executionUrl,
  ]);
});

it("constructed: polling returning 401 stops after a running status without resubmitting the job", async () => {
  const challenge = 'Bearer realm="constructed-service", error="invalid_token"';
  const refusal = reply(statusUrl, {
    type: "about:blank", title: "Unauthorized", status: 401,
    detail: "Access to this job status requires renewed credentials.",
  }, 401, "GET", { "Content-Type": "application/problem+json", "WWW-Authenticate": challenge });
  const transport = recordedFetch(
    ...discovery(), acceptedSubmission(),
    reply(statusUrl, { jobID: "example", processID: processId, type: "process", status: "running", progress: 25 }),
    refusal,
  );
  const client = createClient({ baseUrl, fetch: transport.fetch });
  const execution = await client.execute(processId, { ...payload, mode: "async" });
  expect(execution.kind).toBe("job");
  if (execution.kind !== "job") throw new Error("Expected an accepted job");
  expect(execution.job.statusUrl).toBe(statusUrl);
  const observed: JobStatus[] = [];
  const error = await expectRefusal(client.pollJob(execution.job.statusUrl, {
    intervalMs: 500, timeoutMs: 10_000, maxPolls: 3,
    onStatus: (status) => observed.push(status),
  }), refusal);

  expect(error.envelope.headers.get("www-authenticate")).toBe(challenge);
  expect(observed).toHaveLength(1);
  expect(observed[0]).toMatchObject({ jobId: "example", status: "running", progress: 25, terminal: false });
  transport.assertDone(); // No further poll, results read, dismissal or new execution.
  expectOneSubmission(transport);
  expect(transport.calls.map(([url]) => url)).toEqual([
    baseUrl, `${baseUrl}conformance`, executionUrl, statusUrl, statusUrl,
  ]);
});

it("constructed: results returning 403 preserve the successful job status and reject only the result read", async () => {
  const refusal = reply(resultsUrl, {
    type: "about:blank", title: "Forbidden", status: 403,
    detail: "You do not have permission to read this result.",
  }, 403, "GET", { "Content-Type": "application/problem+json" });
  const transport = recordedFetch(
    ...discovery(), acceptedSubmission(),
    reply(statusUrl, {
      jobID: "example", processID: processId, type: "process", status: "successful", progress: 100,
      links: [{ rel: "http://www.opengis.net/def/rel/ogc/1.0/results", href: resultsUrl, type: "application/json" }],
    }),
    refusal,
  );
  const client = createClient({ baseUrl, fetch: transport.fetch });
  const execution = await client.execute(processId, { ...payload, mode: "async" });
  if (execution.kind !== "job") throw new Error("Expected an accepted job");
  const report = await client.pollJob(execution.job.statusUrl, { timeoutMs: 10_000, maxPolls: 2 });
  expect(report).toMatchObject({ outcome: "terminal", pollCount: 1, statusSequence: ["successful"] });
  const status = report.status;
  if (!status) throw new Error("Expected a successful job status");
  await expectRefusal(client.getResults(execution.job.statusUrl, { status }), refusal);

  expect(status).toMatchObject({ jobId: "example", status: "successful", terminal: true });
  transport.assertDone(); // No guessed result URL, repeated submission or job dismissal.
  expectOneSubmission(transport);
  expect(transport.calls.map(([url]) => url)).toEqual([
    baseUrl, `${baseUrl}conformance`, executionUrl, statusUrl, resultsUrl,
  ]);
});
