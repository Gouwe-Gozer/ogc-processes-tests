import { expect, it } from "vitest";
import { createClient, ProcessesError } from "@breinstein/oap-client";
import { recordedFetch, type readExchange } from "../support/recorded-fetch.js";

// Constructed conversations, not provider captures. See README.md in this folder.
const baseUrl = "https://constructed.test/api/";
const catalogueUrl = `${baseUrl}catalogue`;
const firstPageUrl = `${catalogueUrl}?limit=1`;
const secondPageUrl = `${catalogueUrl}?cursor=second%2Bpage&limit=1`;
const thirdPageUrl = `${baseUrl}catalogue-tail?cursor=last%2Fpage`;
const descriptionUrl = `${baseUrl}descriptions/echo`;
const executionUrl = `${baseUrl}actions/run-echo`;
const statusUrl = `${baseUrl}tasks/example/status`;
const resultsUrl = `${baseUrl}outputs/example?format=json`;
const processId = "constructed-echo";

// Supply inline JSON to the existing transport; there are no files to load.
function reply(url: string, body: unknown, status = 200, method = "GET") {
  return {
    request: { url, method, headers: {} },
    response: {
      status, headers: { "Content-Type": "application/json" }, final_url: url, body,
    },
    // The transport needs a base URL only when a response uses body_file.
    responseFile: new URL(import.meta.url),
  } satisfies Awaited<ReturnType<typeof readExchange>>;
}

function discoveryAndFirstPage() {
  return [
    reply(baseUrl, {
      title: "Constructed pagination service",
      links: [
        { rel: "conformance", href: "conformance", type: "application/json" },
        { rel: "http://www.opengis.net/def/rel/ogc/1.0/processes", href: "catalogue", type: "application/json" },
      ],
    }),
    reply(`${baseUrl}conformance`, {
      conformsTo: ["http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/core"],
    }),
    reply(firstPageUrl, {
      processes: [{ id: "first-process", version: "1.0.0", jobControlOptions: ["sync-execute"] }],
      numberTotal: 3,
      links: [{ rel: "next", href: "?cursor=second%2Bpage&limit=1", type: "application/json" }],
    }),
  ];
}

it("constructed: discovers three pages, runs a process from the last page and retrieves its job result", async () => {
  const payload = { inputs: { message: "Hello from page three" }, response: "document" as const };
  const output = { echo: { value: "Hello from page three" } };
  const submission = reply(executionUrl, {
    jobID: "example", processID: processId, type: "process", status: "accepted",
    links: [{ rel: "monitor", href: statusUrl, type: "application/json" }],
  }, 201, "POST");
  const transport = recordedFetch(
    ...discoveryAndFirstPage(),
    reply(secondPageUrl, {
      processes: [{ id: "second-process", version: "1.0.0", jobControlOptions: ["sync-execute"] }],
      links: [{ rel: "next", href: "catalogue-tail?cursor=last%2Fpage", type: "application/json" }],
    }),
    reply(thirdPageUrl, {
      processes: [{
        id: processId, version: "1.0.0", jobControlOptions: ["async-execute"],
        links: [{ rel: "self", href: "descriptions/echo", type: "application/json" }],
      }],
      links: [],
    }),
    reply(descriptionUrl, {
      id: processId, version: "1.0.0", jobControlOptions: ["async-execute"],
      outputTransmission: ["value"],
      inputs: { message: { title: "Message", minOccurs: 1, maxOccurs: 1, schema: { type: "string" } } },
      outputs: { echo: { title: "Echo", schema: { type: "string" } } },
      links: [{ rel: "http://www.opengis.net/def/rel/ogc/1.0/execute", href: "../actions/run-echo", type: "application/json" }],
    }),
    {
      ...submission,
      response: { ...submission.response, headers: { ...submission.response.headers, Location: statusUrl } },
    },
    reply(statusUrl, { jobID: "example", processID: processId, type: "process", status: "running", progress: 50 }),
    reply(statusUrl, {
      jobID: "example", processID: processId, type: "process", status: "successful", progress: 100,
      links: [{ rel: "http://www.opengis.net/def/rel/ogc/1.0/results", href: "../../outputs/example?format=json", type: "application/json" }],
    }),
    reply(resultsUrl, output),
  );
  // Exercise the public facade with one injected transport for the whole conversation.
  const client = createClient({ baseUrl, fetch: transport.fetch });
  const catalogue = await client.listProcesses({ limit: 1 });
  expect(catalogue.processes.map((process) => process.id)).toEqual(["first-process", "second-process", processId]);
  expect(catalogue).toMatchObject({ pageCount: 3, numberTotal: 3, truncated: false });
  const selected = catalogue.processes.find((process) => process.id === processId);
  if (!selected) throw new Error("The requested process was not found on the last page");

  const description = await client.getProcess(selected.id, { summary: selected });
  expect(description.id).toBe(processId);
  const execution = await client.execute(selected.id, { ...payload, description, mode: "async" });
  expect(execution.kind).toBe("job");
  if (execution.kind !== "job") throw new Error("Expected an asynchronous job");
  expect(execution.job.statusUrl).toBe(statusUrl);
  const submissionCall = transport.calls.find(([, init]) => init?.method === "POST");
  expect(submissionCall?.[0]).toBe(executionUrl);
  expect(JSON.parse(String(submissionCall?.[1]?.body))).toEqual(payload);
  expect(new Headers(submissionCall?.[1]?.headers).get("prefer")).toBe("respond-async");
  expect(new Headers(submissionCall?.[1]?.headers).get("content-type")).toBe("application/json");

  const report = await client.pollJob(execution.job.statusUrl, { intervalMs: 500, timeoutMs: 10_000, maxPolls: 3 });
  expect(report).toMatchObject({ outcome: "terminal", pollCount: 2, statusSequence: ["running", "successful"] });
  const status = report.status;
  if (!status) throw new Error("Expected a final job status");
  expect(status).toMatchObject({ jobId: "example", status: "successful", terminal: true });
  const result = await client.getResults(execution.job.statusUrl, { status });
  expect(result.route).toBe("advertised-link");
  expect(result.url).toBe(resultsUrl);
  expect(result.envelope.status).toBe(200);
  expect(await result.envelope.json()).toEqual(output);

  // Exact ordering also rules out repeated discovery and guessed endpoint paths.
  transport.assertDone();
  expect(transport.calls.map(([url]) => url)).toEqual([
    baseUrl, `${baseUrl}conformance`, firstPageUrl, secondPageUrl, thirdPageUrl,
    descriptionUrl, executionUrl, statusUrl, statusUrl, resultsUrl,
  ]);
});

it("constructed: a second-page HTTP failure rejects the catalogue instead of returning page one as complete", async () => {
  const problem = { type: "about:blank", title: "Service unavailable", status: 503, detail: "The second catalogue page is temporarily unavailable." };
  const failedPage = reply(secondPageUrl, problem, 503);
  const transport = recordedFetch(...discoveryAndFirstPage(), {
    ...failedPage,
    response: { ...failedPage.response, headers: { "Content-Type": "application/problem+json" } },
  });
  const client = createClient({ baseUrl, fetch: transport.fetch });
  const error: unknown = await client.listProcesses({ limit: 1 }).catch((cause: unknown) => cause);

  expect(error).toBeInstanceOf(ProcessesError);
  if (!(error instanceof ProcessesError)) throw new Error("Expected a catalogue failure, not a partial list");
  expect(error.status).toBe(503);
  expect(error.url).toBe(secondPageUrl);
  expect(error.problem).toMatchObject(problem);
  expect(await error.envelope.json()).toEqual(problem);
  transport.assertDone();
  expect(transport.calls.map(([url]) => url)).toEqual([
    baseUrl, `${baseUrl}conformance`, firstPageUrl, secondPageUrl,
  ]);
});
