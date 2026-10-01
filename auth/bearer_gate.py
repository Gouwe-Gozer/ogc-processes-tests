#!/usr/bin/env python3
"""Local test gate: check a fixed Bearer token or API key, then forward to one API."""

import argparse
import hmac
import http.client
import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

REQUEST_HEADERS = {"accept", "accept-language", "content-type", "prefer", "range"}
RESPONSE_HEADERS = {
    "content-type", "content-length", "content-disposition", "content-crs",
    "location", "link", "retry-after", "preference-applied", "www-authenticate",
    "content-range", "accept-ranges", "etag", "last-modified", "content-encoding",
}
METHODS = {"GET", "HEAD", "POST", "DELETE"}
MAX_REQUEST_BYTES = 16 * 1024 * 1024
CHUNK_BYTES = 64 * 1024


class AuthGate(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, upstream, token, origins, timeout=300, *, api_key_header=None):
        target = urlsplit(upstream)
        if (target.scheme not in {"http", "https"} or not target.hostname
                or target.username is not None or target.password is not None
                or target.path not in {"", "/"} or target.query or target.fragment):
            raise ValueError("upstream must be an http(s) origin without a path or credentials")
        self.api_key_mode = api_key_header is not None
        if self.api_key_mode:
            if not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", api_key_header):
                raise ValueError("API-key header must be a nonempty HTTP field name")
            reserved = REQUEST_HEADERS | {
                "authorization", "cookie", "host", "content-length", "transfer-encoding",
                "connection", "origin", "accept-encoding", "expect", "te", "trailer", "upgrade",
            }
            if api_key_header.lower() in reserved or api_key_header.lower().startswith(
                    ("access-control-", "proxy-", "sec-")):
                raise ValueError("choose a custom API-key header, not a protocol or browser-control header")
            if not re.fullmatch(r"[!-~]+", token):
                raise ValueError("the test API key must be nonempty visible ASCII without spaces")
        elif not re.fullmatch(r"[A-Za-z0-9._~+/-]+=*", token):
            raise ValueError("the test token must use Bearer token characters")
        self.credential_header = api_key_header.lower() if self.api_key_mode else "authorization"
        self.upstream = target
        self.upstream_port = target.port  # Validate before starting to listen.
        self.token = token
        self.origins = frozenset(origins)
        self.timeout_seconds = timeout
        super().__init__(address, GateHandler)


class GateHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def setup(self):
        super().setup()
        self.connection.settimeout(self.server.timeout_seconds)

    def log_message(self, _format, *args):
        # BaseHTTPServer logs the full URL. Keep query strings and credentials out.
        pass

    def cors_headers(self):
        self.send_header("Vary", "Origin")
        origin = self.headers.get("Origin")
        if origin in self.server.origins:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Expose-Headers", ", ".join(sorted(RESPONSE_HEADERS)))

    def problem(self, status, title, detail, challenge=None):
        body = json.dumps({"type": "about:blank", "title": title,
                           "status": status, "detail": detail}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/problem+json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        if challenge:
            self.send_header("WWW-Authenticate", challenge)
        self.cors_headers()
        self.end_headers()
        self.close_connection = True
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_OPTIONS(self):
        # Browsers send the preflight without the credential.
        origin = self.headers.get("Origin")
        method = self.headers.get("Access-Control-Request-Method", "")
        requested = {name.strip().lower() for name in
                     self.headers.get("Access-Control-Request-Headers", "").split(",") if name.strip()}
        if (origin not in self.server.origins or method not in METHODS
                or not requested <= REQUEST_HEADERS | {self.server.credential_header}):
            self.problem(403, "Forbidden", "This preflight is not allowed by the test gate.")
            return
        self.send_response(204)
        self.cors_headers()
        self.send_header("Access-Control-Allow-Methods", ", ".join(sorted(METHODS)))
        self.send_header("Access-Control-Allow-Headers", ", ".join(sorted(REQUEST_HEADERS | {self.server.credential_header})))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True

    def forward(self):
        values = self.headers.get_all(self.server.credential_header, [])
        if self.server.api_key_mode:
            if len(values) != 1 or not hmac.compare_digest(values[0].encode(), self.server.token.encode()):
                self.problem(403, "Forbidden", "Supply the configured test API key.")
                return
        else:
            scheme, _, credential = values[0].partition(" ") if len(values) == 1 else ("", "", "")
            if scheme.lower() != "bearer" or not hmac.compare_digest(
                    credential.encode(), self.server.token.encode()):
                challenge = 'Bearer realm="ogc-test"'
                if values:
                    challenge += ', error="invalid_token"'
                self.problem(401, "Unauthorized", "Supply the configured test Bearer token.", challenge)
                return
        # Only origin-form paths: the caller cannot choose another upstream.
        raw_target = self.requestline.split()[1]
        if not raw_target.startswith("/") or raw_target.startswith("//"):
            self.problem(400, "Bad Request", "Use a path under this gate.")
            return
        if self.headers.get("Transfer-Encoding") is not None:
            self.problem(400, "Bad Request", "Send a Content-Length for request bodies.")
            return
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) > 1 or (lengths and not re.fullmatch(r"[0-9]+", lengths[0])):
            self.problem(400, "Bad Request", "Invalid Content-Length.")
            return
        length = int(lengths[0]) if lengths else 0
        if length > MAX_REQUEST_BYTES:
            self.problem(413, "Content Too Large", "Request bodies are limited to 16 MiB.")
            return
        target = self.server.upstream
        connection_type = http.client.HTTPSConnection if target.scheme == "https" else http.client.HTTPConnection
        connection = connection_type(target.hostname, self.server.upstream_port,
                                     timeout=self.server.timeout_seconds)
        started = False
        try:
            body = self.rfile.read(length) if length else None
            if body is not None and len(body) != length:
                self.problem(400, "Bad Request", "Incomplete request body.")
                return
            headers = {name: value for name, value in self.headers.items()
                       if name.lower() in REQUEST_HEADERS and name.lower() != self.server.credential_header}
            # The gate consumes the credential. It is never sent to the backend.
            headers["Accept-Encoding"] = "identity"
            connection.request(self.command, self.path, body=body, headers=headers)
            response = connection.getresponse()  # No redirect following or retries.
            self.send_response(response.status)
            started = True
            for name, value in response.getheaders():
                if name.lower() in RESPONSE_HEADERS:
                    # http.client decodes chunk framing; supply our own framing below.
                    if name.lower() == "content-length" and response.chunked:
                        continue
                    self.send_header(name, value)
            has_body = self.command != "HEAD" and response.status not in {204, 304} and response.status >= 200
            chunked = has_body and (response.chunked or response.getheader("Content-Length") is None)
            if chunked:
                self.send_header("Transfer-Encoding", "chunked")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.cors_headers()
            self.end_headers()
            self.close_connection = True
            if has_body:
                while chunk := response.read(CHUNK_BYTES):
                    if chunked:
                        self.wfile.write(f"{len(chunk):x}\r\n".encode())
                    self.wfile.write(chunk)
                    if chunked:
                        self.wfile.write(b"\r\n")
                if chunked:
                    self.wfile.write(b"0\r\n\r\n")
        except (OSError, http.client.HTTPException):
            if not started:
                self.problem(502, "Bad Gateway", "The configured backend did not provide a response.")
            # After response headers, close the incomplete stream without a success terminator.
            self.close_connection = True
        finally:
            connection.close()

    do_GET = do_HEAD = do_POST = do_DELETE = forward


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--auth", choices=["bearer", "api-key"], default="bearer",
                        help="credential mode (default: bearer)")
    parser.add_argument("--api-key-header", help="key header in api-key mode (default: X-API-Key)")
    parser.add_argument("--upstream", default="http://127.0.0.1:5012")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5002)
    parser.add_argument("--origin", action="append", help="allowed browser origin; repeat as needed")
    parser.add_argument("--timeout", type=float, default=300, help="socket timeout in seconds")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("timeout must be positive")
    if args.auth == "bearer" and args.api_key_header is not None:
        parser.error("--api-key-header requires --auth api-key")
    api_key_header = None
    if args.auth == "api-key":
        api_key_header = args.api_key_header if args.api_key_header is not None else "X-API-Key"
        token = os.environ.get("OGC_TEST_API_KEY", "local-test-api-key")
    else:
        token = os.environ.get("OGC_TEST_BEARER_TOKEN", "local-test-token")
    try:
        server = AuthGate((args.host, args.port), args.upstream, token,
                          args.origin or ["http://localhost:5173"], args.timeout,
                          api_key_header=api_key_header)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(f"{args.auth} test gate: http://{args.host}:{server.server_port} -> {args.upstream}", flush=True)
    print(f"Credential header: {server.credential_header}; Ctrl+C stops the gate.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
