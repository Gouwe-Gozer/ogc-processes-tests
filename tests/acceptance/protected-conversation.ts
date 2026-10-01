import assert from "node:assert/strict";
import type { FetchLike } from "@breinstein/oap-client";
import { recordedFetch } from "../support/recorded-fetch.js";
import { reply } from "./exchanges.js";

// This is the SERVICE side of the fake transport. It inspects credentials;
// it never adds credentials or follows pages on the client's behalf.
export function protectedConversation(
  origin: string,
  credential: { header: string; value: string; status: number; challenge?: string },
  ...exchanges: ReturnType<typeof reply>[]
) {
  const transport = recordedFetch(...exchanges);
  const calls: Parameters<FetchLike>[] = [];
  const fetch: FetchLike = async (url, init = {}) => {
    calls.push([url, init]);
    const target = new URL(url);
    const headers = new Headers(init.headers);
    // The configured test secret belongs in a header, never in the URL.
    const secret = credential.header.toLowerCase() === "authorization"
      ? credential.value.replace(/^Bearer /i, "") : credential.value;
    assert.ok(!decodeURIComponent(url).includes(secret), "Credential leaked into a URL");
    if (target.origin !== origin) {
      assert.equal(headers.get(credential.header), null, "Service credential leaked to another origin");
      assert.equal(headers.get("authorization"), null, "Authorization leaked to another origin");
    } else if (headers.get(credential.header) !== credential.value) {
      const body = { type: "about:blank", title: "Access denied", status: credential.status, detail: "Supply the configured service credential." };
      const response = new Response(JSON.stringify(body), {
        status: credential.status,
        headers: {
          "Content-Type": "application/problem+json",
          ...(credential.challenge ? {
            "WWW-Authenticate": credential.challenge + (headers.has(credential.header) ? ', error="invalid_token"' : ""),
          } : {}),
        },
      });
      Object.defineProperty(response, "url", { value: url });
      return response;
    }
    return transport.fetch(url, init);
  };
  return { fetch, calls, assertDone: transport.assertDone };
}
