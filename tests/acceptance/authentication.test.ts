import { expect, it } from "vitest";
import { createClient, ProcessesError } from "@breinstein/oap-client";
import { authenticatedClient } from "./oap-auth-binding.js";
import { protectedConversation } from "./protected-conversation.js";
import { reply } from "./exchanges.js";

const base = "https://protected.test/api/";
const origin = new URL(base).origin;
const catalogue = base + "processes";
const nextPage = catalogue + "?cursor=protected%2Bpage";
const descriptionUrl = catalogue + "/example";
const executeUrl = descriptionUrl + "/execution";
const jobUrl = base + "jobs/example";
const resultUrl = jobUrl + "/results";
const outsideResultUrl = "https://downloads.test/example.csv?signature=public-example";
const csv = "date,value\n2026-09-15,42\n";
const inputs = { day: "2026-09-15" };

// OpenAPI permits a service to choose its API-key header name. This example
// deliberately does not depend on the commonly used X-API-Key spelling.
const credentials = [
  { name: "Bearer", header: "Authorization", value: "Bearer public-test-token", status: 401,
    challenge: 'Bearer realm="acceptance"' },
  { name: "API key", header: "X-Processing-Key", value: "public-test-api-key", status: 403 },
];

function discovery() {
  return [
    reply(base, { links: [
      { rel: "conformance", href: "conformance", type: "application/json" },
      { rel: "http://www.opengis.net/def/rel/ogc/1.0/processes", href: "processes", type: "application/json" },
    ] }),
    reply(base + "conformance", { conformsTo: ["http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/core"] }),
    reply(catalogue, { processes: [{ id: "first", version: "1.0.0" }], links: [
      { rel: "self", href: catalogue }, { rel: "next", href: "?cursor=protected%2Bpage" },
    ] }),
    reply(nextPage, { processes: [{
      id: "example", version: "1.0.0", jobControlOptions: ["async-execute"],
      links: [{ rel: "self", href: descriptionUrl, type: "application/json" }],
    }], links: [{ rel: "self", href: nextPage }] }),
  ];
}

function throughRunning() {
  return [
    ...discovery(),
    reply(descriptionUrl, {
      id: "example", version: "1.0.0", jobControlOptions: ["async-execute"],
      inputs: { day: { title: "Day", schema: { type: "string", format: "date" } } },
      outputs: { report: { schema: { type: "string", contentMediaType: "text/csv" } } },
      links: [{ rel: "http://www.opengis.net/def/rel/ogc/1.0/execute", href: executeUrl }],
    }),
    reply(executeUrl, { jobID: "example", type: "process", status: "accepted" }, 201, "POST", {
      Location: jobUrl, "Preference-Applied": "respond-async",
    }),
    reply(jobUrl, { jobID: "example", processID: "example", type: "process", status: "running", progress: 50 }),
  ];
}

async function submit(client: ReturnType<typeof createClient>) {
  const processes = await client.listProcesses();
  expect(processes.processes.map((process) => process.id)).toEqual(["first", "example"]);
  const summary = processes.processes.find((process) => process.id === "example")!;
  const description = await client.getProcess(summary.id, { summary });
  const execution = await client.execute(summary.id, { inputs, description, mode: "async" });
  expect(execution.kind).toBe("job");
  if (execution.kind !== "job") throw new Error("The service accepted an asynchronous job");
  expect(execution.job.statusUrl).toBe(jobUrl);
  return execution;
}

it.each(credentials)("$name: a caller-supplied header is sent by the real low-level client; missing and wrong values are refused", async (credential) => {
  const transport = protectedConversation(origin, credential,
    reply(catalogue, { processes: [], links: [{ rel: "self", href: catalogue }] }),
  );
  const client = createClient({ baseUrl: base, fetch: transport.fetch });
  const missing = await client.send(catalogue);
  const wrongValue = credential.name === "Bearer" ? "Bearer wrong" : "wrong";
  const wrong = await client.send(catalogue, { headers: { [credential.header]: wrongValue } });
  const accepted = await client.send(catalogue, { headers: { [credential.header]: credential.value } });
  expect(missing.status).toBe(credential.status);
  expect(wrong.status).toBe(credential.status);
  expect(await wrong.json()).toMatchObject({ status: credential.status, title: "Access denied" });
  if (credential.challenge) expect(missing.headers.get("www-authenticate")).toBe(credential.challenge);
  expect(accepted.status).toBe(200);
  expect(await accepted.json()).toMatchObject({ processes: [] });
  expect(transport.calls).toHaveLength(3);
  transport.assertDone();
});

for (const external of [false, true]) {
  it.each(credentials)(
    "$name: configured credentials support discovery, pagination, execution, polling and " +
    (external ? "a result on another origin without leaking the credential" : "a protected CSV result"),
    async (credential) => {
      const target = external ? outsideResultUrl : resultUrl;
      const transport = protectedConversation(origin, credential,
        ...throughRunning(),
        reply(jobUrl, { jobID: "example", processID: "example", type: "process", status: "successful", links: [
          { rel: "http://www.opengis.net/def/rel/ogc/1.0/results", href: target, type: "text/csv" },
        ] }),
        reply(target, csv, 200, "GET", { "Content-Type": "text/csv" }),
      );
      const client = authenticatedClient(base, transport.fetch, credential);
      await submit(client);
      const report = await client.pollJob(jobUrl, { intervalMs: 500, maxPolls: 3, timeoutMs: 10_000 });
      expect(report.statusSequence).toEqual(["running", "successful"]);
      expect(report.outcome).toBe("terminal");
      if (!report.status) throw new Error("Expected the successful job status");
      const result = await client.getResults(jobUrl, { status: report.status });
      expect(result.url).toBe(target);
      expect(await result.envelope.text()).toBe(csv);
      const post = transport.calls.filter(([, init]) => init?.method === "POST");
      expect(post).toHaveLength(1);
      expect(JSON.parse(String(post[0]![1]?.body)).inputs).toEqual(inputs);
      expect(new Headers(post[0]![1]?.headers).get("prefer")).toBe("respond-async");
      expect(transport.calls).toHaveLength(9);
      for (const [url, init] of transport.calls) {
        expect(new Headers(init?.headers).get(credential.header))
          .toBe(new URL(url).origin === origin ? credential.value : null);
      }
      transport.assertDone();
    },
  );
}

it.each(credentials)("$name: a wrong configured credential stops discovery with the service explanation", async (credential) => {
  const transport = protectedConversation(origin, credential);
  const wrongValue = credential.name === "Bearer" ? "Bearer wrong" : "wrong";
  const client = authenticatedClient(base, transport.fetch, { header: credential.header, value: wrongValue });
  const error: unknown = await client.listProcesses().catch((cause: unknown) => cause);
  expect(error).toBeInstanceOf(ProcessesError);
  if (!(error instanceof ProcessesError)) throw new Error("Expected the service's credential refusal");
  expect(error.status).toBe(credential.status);
  expect(error.problem?.detail).toBe("Supply the configured service credential.");
  expect(transport.calls).toHaveLength(1);
  expect(new Headers(transport.calls[0]![1]?.headers).get(credential.header)).toBe(wrongValue);
  if (credential.challenge) expect(error.envelope.headers.get("www-authenticate"))
    .toBe(credential.challenge + ', error="invalid_token"');
  transport.assertDone();
});

it.each(credentials)("$name: access revoked during polling stops without repeating the calculation", async (credential) => {
  const problem = { type: "about:blank", title: "Access revoked", status: credential.status, detail: "This credential no longer grants access." };
  const challenge = credential.challenge ? { "WWW-Authenticate": credential.challenge + ', error="invalid_token"' } : {};
  const transport = protectedConversation(origin, credential,
    ...throughRunning(),
    reply(jobUrl, problem, credential.status, "GET", { "Content-Type": "application/problem+json", ...challenge }),
  );
  const client = authenticatedClient(base, transport.fetch, credential);
  await submit(client);
  const error: unknown = await client.pollJob(jobUrl, { intervalMs: 500, maxPolls: 3, timeoutMs: 10_000 })
    .catch((cause: unknown) => cause);
  expect(error).toBeInstanceOf(ProcessesError);
  if (!(error instanceof ProcessesError)) throw new Error("Expected the polling refusal to be reported");
  expect(error.status).toBe(credential.status);
  expect(error.problem?.detail).toBe(problem.detail);
  if (credential.challenge) expect(error.envelope.headers.get("www-authenticate"))
    .toBe(credential.challenge + ', error="invalid_token"');
  expect(transport.calls.filter(([, init]) => init?.method === "POST")).toHaveLength(1);
  expect(transport.calls).toHaveLength(8);
  for (const [, init] of transport.calls) {
    expect(new Headers(init?.headers).get(credential.header)).toBe(credential.value);
  }
  transport.assertDone();
});
