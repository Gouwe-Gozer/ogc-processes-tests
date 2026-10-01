"""Tests of the gate's real HTTP boundary, not of OAP or a real OGC provider."""

import http.client
import json
import threading
import unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from bearer_gate import BearerGate, MAX_REQUEST_BYTES

ORIGIN = "http://localhost:5173"
TOKEN = "local-test-token"


@contextmanager
def running(server):
    thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=0.01), daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


class Backend(BaseHTTPRequestHandler):
    # This test-only HTTP endpoint returns fixed bytes; it has no OGC implementation.
    def respond(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        self.server.calls.append((self.command, self.path, dict(self.headers), body))
        self.send_response(self.server.status)
        for name, value in self.server.headers.items():
            self.send_header(name, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(self.server.body)

    do_GET = do_HEAD = do_POST = do_DELETE = respond

    def log_message(self, *_args):
        pass


class GateTests(unittest.TestCase):
    def setUp(self):
        backend = ThreadingHTTPServer(("127.0.0.1", 0), Backend)
        backend.calls = []
        backend.status = 200
        backend.body = b'{"ok":true}'
        backend.headers = {"Content-Type": "application/json", "Content-Length": str(len(backend.body))}
        self.backend = self.enterContext(running(backend))
        upstream = f"http://127.0.0.1:{backend.server_port}"
        self.gate = self.enterContext(running(BearerGate(("127.0.0.1", 0), upstream, TOKEN, [ORIGIN], 2)))

    def request(self, path="/processes", method="GET", body=None, headers=None, authorized=True):
        request_headers = {"Origin": ORIGIN}
        if authorized:
            request_headers["Authorization"] = f"Bearer {TOKEN}"
        request_headers.update(headers or {})
        connection = http.client.HTTPConnection("127.0.0.1", self.gate.server_port, timeout=3)
        try:
            connection.request(method, path, body, request_headers)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_missing_and_wrong_credentials_never_reach_backend(self):
        for authorization in [None, "Bearer wrong", f"Basic {TOKEN}", "Bearer LOCAL-TEST-TOKEN"]:
            with self.subTest(authorization=authorization):
                headers = {} if authorization is None else {"Authorization": authorization}
                status, headers, body = self.request(authorized=False, headers=headers)
                self.assertEqual(status, 401)
                self.assertEqual(json.loads(body)["status"], 401)
                self.assertIn('Bearer realm="ogc-test"', headers["WWW-Authenticate"])
                self.assertEqual(headers["Access-Control-Allow-Origin"], ORIGIN)
                self.assertIn("www-authenticate", headers["Access-Control-Expose-Headers"])
        self.assertEqual(self.backend.calls, [])

    def test_authorized_get_preserves_path_query_and_consumes_credentials(self):
        self.assertEqual(self.request("/jobs?cursor=a%2Bb", headers={"Cookie": "session=secret"})[0], 200)
        method, path, headers, _ = self.backend.calls[0]
        self.assertEqual((method, path), ("GET", "/jobs?cursor=a%2Bb"))
        self.assertNotIn("Authorization", headers)
        self.assertNotIn("Cookie", headers)
        self.assertNotIn("Origin", headers)

    def test_post_is_forwarded_once_with_body_prefer_and_location(self):
        self.backend.status = 201
        self.backend.headers["Location"] = "http://localhost:5002/jobs/example"
        payload = b'{"inputs":{"message":"hello"}}'
        status, headers, body = self.request("/processes/echo/execution", "POST", payload,
            {"Content-Type": "application/json", "Prefer": "respond-async"})
        self.assertEqual(status, 201)
        self.assertEqual(headers["Location"], "http://localhost:5002/jobs/example")
        self.assertEqual(body, self.backend.body)
        self.assertEqual(len(self.backend.calls), 1)
        method, path, sent, actual_body = self.backend.calls[0]
        self.assertEqual((method, path, actual_body), ("POST", "/processes/echo/execution", payload))
        self.assertEqual(sent["Prefer"], "respond-async")
        self.assertEqual(sent["Content-Type"], "application/json")

    def test_backend_403_is_preserved_without_retry(self):
        self.backend.status = 403
        self.backend.body = b'{"title":"Forbidden","status":403}'
        self.backend.headers = {"Content-Type": "application/problem+json", "Content-Length": str(len(self.backend.body))}
        status, _, body = self.request("/jobs/example/results")
        self.assertEqual(status, 403)
        self.assertEqual(body, self.backend.body)
        self.assertEqual(len(self.backend.calls), 1)

    def test_redirect_is_returned_not_followed(self):
        self.backend.status = 302
        self.backend.headers["Location"] = "https://elsewhere.invalid/result"
        status, headers, _ = self.request()
        self.assertEqual((status, headers["Location"]), (302, "https://elsewhere.invalid/result"))
        self.assertEqual(len(self.backend.calls), 1)

    def test_large_binary_body_survives_with_and_without_length(self):
        self.backend.body = bytes(range(256)) * 4096
        for declared_length in [True, False]:
            with self.subTest(declared_length=declared_length):
                self.backend.headers = {"Content-Type": "application/octet-stream"}
                if declared_length:
                    self.backend.headers["Content-Length"] = str(len(self.backend.body))
                status, _, body = self.request("/jobs/example/results")
                self.assertEqual(status, 200)
                self.assertEqual(body, self.backend.body)

    def test_head_and_delete(self):
        status, headers, body = self.request(method="HEAD")
        self.assertEqual((status, body), (200, b""))
        self.assertEqual(headers["Content-Length"], str(len(self.backend.body)))
        self.backend.status = 204
        self.backend.body = b""
        self.backend.headers = {}
        self.assertEqual(self.request("/jobs/example", "DELETE")[0], 204)
        self.assertEqual([call[0] for call in self.backend.calls], ["HEAD", "DELETE"])

    def test_preflight_works_without_token_and_without_contacting_backend(self):
        status, headers, body = self.request(method="OPTIONS", authorized=False, headers={
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization, content-type, prefer",
        })
        self.assertEqual((status, body), (204, b""))
        self.assertEqual(headers["Access-Control-Allow-Origin"], ORIGIN)
        self.assertIn("authorization", headers["Access-Control-Allow-Headers"])
        self.assertEqual(self.backend.calls, [])

    def test_preflight_rejects_unconfigured_origins_methods_and_headers(self):
        for change in [{"Origin": "https://elsewhere.invalid"},
                       {"Access-Control-Request-Method": "PUT"},
                       {"Access-Control-Request-Headers": "x-api-key"}]:
            with self.subTest(change=change):
                status, _, _ = self.request(method="OPTIONS", authorized=False, headers={
                    "Access-Control-Request-Method": "GET", **change,
                })
                self.assertEqual(status, 403)
        self.assertEqual(self.backend.calls, [])

    def test_gate_owns_cors_headers_and_does_not_forward_set_cookie(self):
        self.backend.headers.update({"Access-Control-Allow-Origin": "*", "Set-Cookie": "secret=1"})
        _, headers, _ = self.request(headers={"Origin": "https://elsewhere.invalid"})
        self.assertNotIn("Access-Control-Allow-Origin", headers)
        self.assertNotIn("Set-Cookie", headers)

    def test_bad_targets_and_request_framing_do_not_reach_backend(self):
        for path, headers, expected in [
            ("http://elsewhere.invalid/data", {}, 400),
            ("//elsewhere.invalid/data", {}, 400),
            ("/", {"Content-Length": "-1"}, 400),
            ("/", {"Transfer-Encoding": "chunked"}, 400),
            ("/", {"Content-Length": str(MAX_REQUEST_BYTES + 1)}, 413),
        ]:
            with self.subTest(path=path, headers=headers):
                self.assertEqual(self.request(path, headers=headers)[0], expected)
        self.assertEqual(self.backend.calls, [])

    def test_backend_connection_failure_returns_502(self):
        # Reserve a port without listening: connection refused, not a flaky live API.
        import socket
        with socket.socket() as unused:
            unused.bind(("127.0.0.1", 0))
            self.gate.upstream_port = unused.getsockname()[1]
            status, headers, body = self.request()
        self.assertEqual(status, 502)
        self.assertEqual(json.loads(body)["status"], 502)
        self.assertEqual(headers["Access-Control-Allow-Origin"], ORIGIN)


if __name__ == "__main__":
    unittest.main()
