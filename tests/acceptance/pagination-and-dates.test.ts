import { expect, it } from "vitest";
import { createClient, execute, listJobs, listProcesses, ProcessesError } from "@breinstein/oap-client";
import { recordedFetch } from "../support/recorded-fetch.js";
import { reply } from "./exchanges.js";

const base = "https://acceptance.test/api/";
const jobsUrl = base + "jobs";
const processesUrl = base + "processes";
const job = (id: string, created = "2026-09-15T10:00:00Z") => ({
  jobID: id, processID: "date-example", type: "process", status: "successful", created, links: [],
});

it("finds the advertised job list and follows opaque next links through an empty final page", async () => {
  const first = jobsUrl + "?limit=2";
  const second = jobsUrl + "?cursor=next%2Bbatch%2F&limit=2";
  const third = base + "job-pages/end?cursor=finished%3D";
  const transport = recordedFetch(
    reply(base, { links: [
      { rel: "conformance", href: "conformance", type: "application/json" },
      { rel: "http://www.opengis.net/def/rel/ogc/1.0/job-list", href: "jobs", type: "application/json" },
    ] }),
    reply(base + "conformance", { conformsTo: [
      "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/core",
      "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/job-list",
    ] }),
    reply(first, { jobs: [job("one"), job("two")], links: [
      { rel: "self", href: first }, { rel: "next", href: "?cursor=next%2Bbatch%2F&limit=2" },
    ] }),
    reply(second, { jobs: [job("three")], links: [
      { rel: "self", href: second }, { rel: "next", href: "job-pages/end?cursor=finished%3D" },
    ] }),
    reply(third, { jobs: [], links: [{ rel: "self", href: third }] }),
  );
  const client = createClient({ baseUrl: base, fetch: transport.fetch });
  const result = await client.listJobs({ limit: 2 });
  expect(result.jobs.map((entry) => entry.jobId)).toEqual(["one", "two", "three"]);
  expect(result.truncated).toBe(false);
  transport.assertDone();
});

it.each(["processes", "jobs"] as const)(
  "%s pagination follows a next link supplied in the HTTP Link header",
  async (kind) => {
    const first = base + kind;
    const second = first + "?cursor=header%2Bonly";
    const entries = kind === "jobs"
      ? [job("one"), job("two")]
      : [{ id: "one", version: "1.0.0" }, { id: "two", version: "1.0.0" }];
    const transport = recordedFetch(
      reply(first, { [kind]: [entries[0]], links: [{ rel: "self", href: first }] }, 200, "GET", {
        Link: '<?cursor=header%2Bonly>; rel="next"; type="application/json"',
      }),
      reply(second, { [kind]: [entries[1]], links: [{ rel: "self", href: second }] }),
    );
    if (kind === "jobs") {
      expect((await listJobs(first, { fetch: transport.fetch })).jobs.map((entry) => entry.jobId))
        .toEqual(["one", "two"]);
    } else {
      expect((await listProcesses(first, { fetch: transport.fetch })).processes.map((entry) => entry.id))
        .toEqual(["one", "two"]);
    }
    transport.assertDone();
  },
);

it("a failed later job page cannot be returned as a complete list", async () => {
  const second = jobsUrl + "?cursor=next";
  const problem = { type: "about:blank", title: "Service unavailable", status: 503, detail: "Next job page unavailable." };
  const transport = recordedFetch(
    reply(jobsUrl, { jobs: [job("one")], links: [{ rel: "next", href: second }] }),
    reply(second, problem, 503, "GET", { "Content-Type": "application/problem+json" }),
  );
  const error: unknown = await listJobs(jobsUrl, { fetch: transport.fetch }).catch((cause: unknown) => cause);
  expect(error).toBeInstanceOf(ProcessesError);
  if (!(error instanceof ProcessesError)) throw new Error("Expected the failed page to reject listing");
  expect(error.status).toBe(503);
  expect(error.url).toBe(second);
  expect(error.problem?.detail).toBe(problem.detail);
  transport.assertDone();
});

const dateCases = [
  { name: "instant", datetime: "2026-09-15T10:00:00Z", created: "2026-09-15T10:00:00Z" },
  { name: "closed interval", datetime: "2026-09-01T00:00:00Z/2026-10-01T00:00:00Z", created: "2026-09-15T10:00:00Z" },
  { name: "open start", datetime: "../2026-10-01T00:00:00Z", created: "2026-09-15T10:00:00Z" },
  { name: "open end", datetime: "2026-09-01T00:00:00Z/..", created: "2026-09-15T10:00:00Z" },
  { name: "positive timezone offset", datetime: "2026-09-15T12:00:00+02:00", created: "2026-09-15T10:00:00Z" },
];

it.each(dateCases)("job datetime: preserves a supplied $name and follows the server's filtered cursor", async ({ datetime, created }) => {
  // This public function accepts a URL. The caller supplies the initial filter;
  // the client must preserve it, then follow next without rebuilding the query.
  const first = jobsUrl + "?" + new URLSearchParams({ datetime, limit: "1" }).toString();
  const second = jobsUrl + "?cursor=filtered%2Bselection%2F";
  const transport = recordedFetch(
    reply(first, { jobs: [job("one", created)], links: [
      { rel: "self", href: first }, { rel: "next", href: "?cursor=filtered%2Bselection%2F" },
    ] }),
    reply(second, { jobs: [job("two", created)], links: [{ rel: "self", href: second }] }),
  );
  const result = await listJobs(first, { fetch: transport.fetch });
  expect(result.jobs.map((entry) => entry.jobId)).toEqual(["one", "two"]);
  expect(result.jobs.map((entry) => entry.created)).toEqual([created, created]);
  expect(result.truncated).toBe(false);
  expect(new URL(transport.calls[0]![0]).searchParams.get("datetime")).toBe(datetime);
  // A server may carry the selection inside its opaque cursor, with no datetime
  // parameter repeated. Adding the original query would change that advertised URL.
  expect(transport.calls.map(([url]) => url)).toEqual([first, second]);
  transport.assertDone();
});

it("a date filter with no matches returns an empty list without an extra page request", async () => {
  const url = jobsUrl + "?datetime=1900-01-01T00%3A00%3A00Z";
  const transport = recordedFetch(reply(url, { jobs: [], links: [{ rel: "self", href: url }] }));
  const result = await listJobs(url, { fetch: transport.fetch });
  expect(result.jobs).toEqual([]);
  expect(result.truncated).toBe(false);
  transport.assertDone();
});

it("keeps an invalid datetime service error instead of retrying without the filter", async () => {
  const url = jobsUrl + "?datetime=not-a-date";
  const problem = { type: "about:blank", title: "Invalid datetime", status: 400, detail: "Use a date-time or an interval." };
  const transport = recordedFetch(reply(url, problem, 400, "GET", { "Content-Type": "application/problem+json" }));
  const error: unknown = await listJobs(url, { fetch: transport.fetch }).catch((cause: unknown) => cause);
  expect(error).toBeInstanceOf(ProcessesError);
  if (!(error instanceof ProcessesError)) throw new Error("Expected the invalid filter to be reported");
  expect(error.status).toBe(400);
  expect(error.problem?.detail).toBe(problem.detail);
  transport.assertDone();
});

it("sends date and date-time process inputs unchanged in the execution body", async () => {
  const inputs = { day: "2026-09-15", start: "2026-09-15T12:00:00+02:00", end: "2026-09-15T13:30:00+02:00" };
  const url = processesUrl + "/date-example/execution";
  const transport = recordedFetch(reply(url, { received: inputs }, 200, "POST"));
  const result = await execute(processesUrl, "date-example", { inputs, fetch: transport.fetch });
  expect(result.kind).toBe("immediate");
  expect(JSON.parse(String(transport.calls[0]![1]?.body)).inputs).toEqual(inputs);
  expect(new Headers(transport.calls[0]![1]?.headers).get("content-type")).toBe("application/json");
  transport.assertDone();
});
