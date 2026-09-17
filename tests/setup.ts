import { afterEach, beforeEach, expect, vi } from "vitest";

// The real client must use the injected fetch, including during discovery.
// Check calls afterwards too: the client may catch a fetch rejection.
beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn(() => {
    throw new Error("Live fetch is disabled. Inject the recorded fetch into the client.");
  }));
});

afterEach(() => {
  try {
    expect(globalThis.fetch, "A test attempted live HTTP").not.toHaveBeenCalled();
  } finally {
    vi.unstubAllGlobals();
  }
});
