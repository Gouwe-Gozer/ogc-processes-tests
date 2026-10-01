import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { onTestFinished } from "vitest";
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

function setupError(context: string, cause: unknown): Error {
  const detail = cause instanceof Error ? cause.message : String(cause);
  const error = new Error(`[TEST SETUP] ${context}: ${detail}`, { cause });
  error.name = "FixtureSetupError";
  return error;
}

class ClientRequestMismatch extends Error {
  constructor(message: string) {
    super("[CLIENT REQUEST] " + message);
    this.name = "ClientRequestMismatch";
  }
}

async function readCapture(file: URL, variables: Readonly<Record<string, string>>) {
  try {
    const source = await readFile(file, "utf8");
    const expanded = source.replace(/\{\{([^{}]+)\}\}/g, (_token, name: string) => {
      const value = Object.hasOwn(variables, name) ? variables[name] : undefined;
      if (value === undefined) throw new Error(`Unresolved fixture variable ${name}`);
      return JSON.stringify(value).slice(1, -1);
    });
    return JSON.parse(expanded) as unknown;
  } catch (cause) {
    throw setupError(`Cannot load capture ${file.pathname}`, cause);
  }
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
  let replayFailure: Error | undefined;
  // Report the original diagnostic even when the client wraps or catches it.
  // This belongs to the current client test; it does not add a helper test.
  onTestFinished(() => {
    if (replayFailure) throw replayFailure;
  });

  const fetch: FetchLike = async (url, init = {}) => {
    calls.push([url, init]);
    const exchange = exchanges[next];
    const step = next + 1;
    try {
      if (!exchange) {
        throw new ClientRequestMismatch(`Unexpected request ${step}: ${init.method ?? "GET"} ${url}; no reply remains`);
      }
      // Check only the fields this replay is about to use.
      assert.equal(typeof exchange.request.url, "string", "Capture request URL must be a string");
      assert.equal(typeof exchange.request.method, "string", "Capture request method must be a string");
      assert.ok(exchange.request.url && exchange.request.method, "Capture request URL and method must not be empty");
      new URL(exchange.request.url);
      const expected = `${exchange.request.method.toUpperCase()} ${exchange.request.url}`;
      const actual = `${String(init?.method ?? "GET").toUpperCase()} ${url}`;
      if (actual !== expected) {
        throw new ClientRequestMismatch(`Request ${step}: expected ${expected}; received ${actual}`);
      }
      const capture = exchange.response;
      assert.ok(Number.isInteger(capture.status), "Capture response status must be an integer");
      assert.equal(typeof capture.final_url, "string", "Capture final URL must be a string");
      new URL(capture.final_url);
      assert.ok(capture.headers && typeof capture.headers === "object", "Capture response headers are missing");
      if (capture.body_file !== undefined) {
        assert.ok(typeof capture.body_file === "string" && capture.body_file.length > 0, "body_file must be a nonempty path");
      }
      // Strings are raw text; other values are parsed JSON. body_file retains bytes.
      const body = capture.body_file !== undefined
        ? new Uint8Array(await readFile(new URL(capture.body_file, exchange.responseFile)))
        : capture.body === undefined
          ? null
          : typeof capture.body === "string" ? capture.body : JSON.stringify(capture.body);
      const response = new Response(body, { status: capture.status, headers: capture.headers });
      Object.defineProperty(response, "url", { value: capture.final_url });
      next += 1;
      return response;
    } catch (cause) {
      const error = cause instanceof ClientRequestMismatch ? cause
        : setupError(`Cannot replay response ${step} from ${exchange?.responseFile?.pathname ?? "the selected conversation"}`, cause);
      replayFailure ??= error;
      throw error;
    }
  };

  return {
    fetch,
    calls,
    assertDone() {
      if (replayFailure) throw replayFailure;
      if (calls.length !== exchanges.length || next !== exchanges.length) {
        throw new ClientRequestMismatch(
          `Conversation incomplete: expected ${exchanges.length} requests; received ${calls.length}, served ${next}`,
        );
      }
    },
  };
}
