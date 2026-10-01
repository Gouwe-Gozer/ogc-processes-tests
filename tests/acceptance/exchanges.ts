import type { readExchange } from "../support/recorded-fetch.js";

// The same plain HTTP capture shape as existing scenarios, constructed here.
export function reply(
  url: string, body: unknown, status = 200, method = "GET",
  headers: Record<string, string> = {},
): Awaited<ReturnType<typeof readExchange>> {
  return {
    request: { url, method, headers: {} },
    response: {
      status, headers: { "Content-Type": "application/json", ...headers },
      final_url: url, body,
    },
    responseFile: new URL(import.meta.url),
  };
}
