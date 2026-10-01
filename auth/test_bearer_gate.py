"""Tests of the gate's real HTTP boundary, not of OAP or a real OGC provider."""

import http.client
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from bearer_gate import AuthGate, MAX_REQUEST_BYTES

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
    api_key_header = None
    secret = TOKEN
    credential_header = "Authorization"
    credential_value = f"Bearer {TOKEN}"
    denial_status = 401

    def setUp(self):
        backend = ThreadingHTTPServer(("127.0.0.1", 0), Backend)
        backend.calls = []
        backend.status = 200
        backend.body = b'{"ok":true}'
        backend.headers = {"Content-Type": "application/json", "Content-Length": str(len(backend.body))}
        self.backend = self.enterContext(running(backend))
        upstream = f"http://127.0.0.1:{backend.server_port}"
        self.gate = self.enterContext(running(AuthGate(
            ("127.0.0.1", 0), upstream, self.secret, [ORIGIN], 2, api_key_header=self.api_key_header,
        )))

    def request(self, path="/processes", method="GET", body=None, headers=None, authorized=True):
        request_headers = {"Origin": ORIGIN}
        if authorized:
            request_headers[self.credential_header] = self.credential_value
        request_headers.update(headers or {})
        connection = http.client.HTTPConnection("127.0.0.1", self.gate.server_port, timeout=3)
        try:
            connection.request(method, path, body, request_headers)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_missing_and_wrong_credentials_never_reach_backend(self):
        for credential in [None, "wrong", f"Basic {self.secret}", self.credential_value.upper()]:
            with self.subTest(credential=credential):
                headers = {} if credential is None else {self.credential_header: credential}
                status, headers, body = self.request(authorized=False, headers=headers)
                self.assertEqual(status, self.denial_status)
                self.assertEqual(json.loads(body)["status"], self.denial_status)
                if self.api_key_header:
                    self.assertNotIn("WWW-Authenticate", headers)
                else:
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
        self.assertNotIn(self.credential_header.lower(), {name.lower() for name in headers})

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

    def test_preflight_works_without_credential_and_without_contacting_backend(self):
        status, headers, body = self.request(method="OPTIONS", authorized=False, headers={
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": f"{self.credential_header}, content-type, prefer",
        })
        self.assertEqual((status, body), (204, b""))
        self.assertEqual(headers["Access-Control-Allow-Origin"], ORIGIN)
        self.assertIn(self.credential_header.lower(), headers["Access-Control-Allow-Headers"])
        self.assertEqual(self.backend.calls, [])

    def test_preflight_rejects_unconfigured_origins_methods_and_headers(self):
        for change in [{"Origin": "https://elsewhere.invalid"},
                       {"Access-Control-Request-Method": "PUT"},
                       {"Access-Control-Request-Headers": "x-unconfigured-key"}]:
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


    def test_duplicate_credentials_are_refused(self):
        connection = http.client.HTTPConnection("127.0.0.1", self.gate.server_port, timeout=3)
        try:
            connection.putrequest("GET", "/processes")
            connection.putheader(self.credential_header, self.credential_value)
            connection.putheader(self.credential_header.lower(), self.credential_value)
            connection.endheaders()
            response = connection.getresponse()
            self.assertEqual(response.status, self.denial_status)
            response.read()
        finally:
            connection.close()
        self.assertEqual(self.backend.calls, [])


class ApiKeyGateTests(GateTests):
    # Every shared forwarding, streaming and failure check also runs in this mode.
    api_key_header = "X-Processing-Key"
    secret = "test:key+with/symbols=_-"
    credential_header = api_key_header
    credential_value = secret
    denial_status = 403

    def test_header_name_is_case_insensitive_and_key_is_consumed(self):
        status, _, _ = self.request(authorized=False, headers={
            self.credential_header.lower(): self.secret,
            "Authorization": f"Bearer {TOKEN}", "Cookie": "session=secret",
        })
        self.assertEqual(status, 200)
        self.assertEqual(len(self.backend.calls), 1)
        headers = {name.lower(): value for name, value in self.backend.calls[0][2].items()}
        self.assertNotIn(self.credential_header.lower(), headers)
        self.assertNotIn("authorization", headers)
        self.assertNotIn("cookie", headers)

    def test_other_credentials_do_not_replace_the_configured_key(self):
        for headers in [{"Authorization": f"Bearer {TOKEN}"}, {"X-API-Key": self.secret}]:
            with self.subTest(headers=headers):
                self.assertEqual(self.request(authorized=False, headers=headers)[0], 403)
        self.assertEqual(self.backend.calls, [])

    def test_preflight_only_allows_the_configured_auth_header(self):
        status, _, _ = self.request(method="OPTIONS", authorized=False, headers={
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization, content-type",
        })
        self.assertEqual(status, 403)
        self.assertEqual(self.backend.calls, [])


class ConfigurationTests(unittest.TestCase):
    def test_cli_rejects_conflicting_mode_empty_header_and_empty_key(self):
        secret = "public-cli-test-secret"
        for arguments, key in [
            (["--api-key-header", "X-Processing-Key"], secret),
            (["--auth", "api-key", "--api-key-header", ""], secret),
            (["--auth", "api-key"], ""),
        ]:
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).with_name("bearer_gate.py")), "--port", "0", *arguments],
                    env={**os.environ, "OGC_TEST_API_KEY": key},
                    capture_output=True, text=True, timeout=3,
                )
                self.assertEqual(result.returncode, 2)
                self.assertNotIn(secret, result.stdout + result.stderr)

    def test_api_key_header_cannot_be_invalid_or_replace_protocol_headers(self):
        for header in ["", "bad header", "x-key\r\nInjected: yes", "x-key:part", "clé",
                       "Authorization", "CONTENT-LENGTH", "Host", "Cookie", "Accept",
                       "Origin", "Connection", "Access-Control-Request-Method", "Sec-Fetch-Site"]:
            with self.subTest(header=header), self.assertRaises(ValueError):
                with AuthGate(("127.0.0.1", 0), "http://127.0.0.1:1", "key", [], api_key_header=header):
                    pass

    def test_api_key_cannot_be_empty_or_contain_whitespace_or_non_ascii(self):
        for key in ["", "white space", "key\nvalue", "key\rvalue", "key\tvalue", "clé"]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                with AuthGate(("127.0.0.1", 0), "http://127.0.0.1:1", key, [], api_key_header="X-API-Key"):
                    pass


if __name__ == "__main__":
    unittest.main()
