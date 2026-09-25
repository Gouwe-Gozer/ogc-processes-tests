import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import type { FetchLike } from "@breinstein/oap-client";

// These describe the existing capture files, not client models or expectations.
interface RequestCapture {
  method: string;
  url: string;
  headers: Record<string, string>;
  body?: unknown;
}

interface ResponseCapture {
  status: number;
  headers: Record<string, string>;
  final_url: string;
  body?: unknown;
  body_file?: string;
}

const scenarios = new URL("../../scenarios/", import.meta.url);

async function readCapture(file: URL, variables: Readonly<Record<string, string>>) {
  const source = await readFile(file, "utf8");
  const expanded = source.replace(/\{\{([^{}]+)\}\}/g, (_token, name: string) => {
    const value = Object.hasOwn(variables, name) ? variables[name] : undefined;
    if (value === undefined) throw new Error(`Unresolved fixture variable ${name} in ${file.pathname}`);
    return JSON.stringify(value).slice(1, -1);
  });
  return JSON.parse(expanded) as unknown;
}

/** Load an explicit pair; responseStep selects a saved variant of the same request. */
export async function readExchange(
  scenario: string,
  step: string,
  variables: Readonly<Record<string, string>> = {},
  responseStep: string = step,
) {
  const requestFile = new URL(`${scenario}/${step}.request.json`, scenarios);
  const responseFile = new URL(`${scenario}/${responseStep}.response.json`, scenarios);
  const [request, response] = await Promise.all([
    readCapture(requestFile, variables),
    readCapture(responseFile, variables),
  ]);
  return {
    request: request as RequestCapture,
    response: response as ResponseCapture,
    responseFile,
  };
}

/** A finite sequence at the client's real fetch boundary. Never calls live fetch. */
export function recordedFetch(...exchanges: Awaited<ReturnType<typeof readExchange>>[]) {
  const calls: Parameters<FetchLike>[] = [];
  let next = 0;

  const fetch: FetchLike = async (url, init = {}) => {
    calls.push([url, init]);
    const exchange = exchanges[next];
    assert.ok(exchange, `Unexpected request: ${init.method ?? "GET"} ${url}`);
    assert.equal(url, exchange.request.url, "Request URL differs from the selected capture");
    assert.equal(
      (init.method ?? "GET").toUpperCase(),
      exchange.request.method.toUpperCase(),
      "Request method differs from the selected capture",
    );
    next += 1;

    const capture = exchange.response;
    // Strings are recorded raw text. Objects, arrays, numbers, booleans and null
    // are parsed JSON. body_file retains bytes when textual reconstruction is insufficient.
    const body = capture.body_file !== undefined
      ? new Uint8Array(await readFile(new URL(capture.body_file, exchange.responseFile)))
      : capture.body === undefined
        ? null
        : typeof capture.body === "string" ? capture.body : JSON.stringify(capture.body);
    const response = new Response(body, { status: capture.status, headers: capture.headers });
    Object.defineProperty(response, "url", { value: capture.final_url });
    return response;
  };

  return {
    fetch,
    calls,
    assertDone() {
      // Count failed attempts too, even if the client caught their rejection.
      assert.equal(calls.length, exchanges.length, "Unexpected or missing recorded requests");
      assert.equal(next, exchanges.length, "Not every recorded exchange was consumed");
    },
  };
}
