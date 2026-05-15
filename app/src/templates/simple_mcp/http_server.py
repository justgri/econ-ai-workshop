from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

try:
    from .mcp_server import handle_jsonrpc_message
except ImportError:  # Allows `python http_server.py` while live-coding.
    from mcp_server import handle_jsonrpc_message  # type: ignore[no-redef]


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_PATH = "/mcp"


def _normalize_path(value: str) -> str:
    path = str(value or "").strip() or DEFAULT_PATH
    if not path.startswith("/"):
        path = f"/{path}"
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    return path


def _is_authorized(headers, *, expected_token: str) -> bool:
    if not expected_token:
        return True
    auth_header = str(headers.get("Authorization", "") or "").strip()
    return auth_header == f"Bearer {expected_token}"


def _json_response(
    handler: BaseHTTPRequestHandler,
    *,
    status: HTTPStatus,
    payload: Any,
) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status.value)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _text_response(
    handler: BaseHTTPRequestHandler,
    *,
    status: HTTPStatus,
    text: str,
) -> None:
    body = text.encode("utf-8")
    handler.send_response(status.value)
    handler.send_header("Content-Type", "text/plain; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def create_handler(*, mcp_path: str, expected_token: str):
    normalized_mcp_path = _normalize_path(mcp_path)

    class SimpleMCPHttpHandler(BaseHTTPRequestHandler):
        server_version = "SimpleMCP/0.1"

        def log_message(self, *_: object) -> None:
            return

        def do_GET(self) -> None:  # noqa: N802
            path = (urlparse(self.path).path or "").strip()
            if path in {"/health", "/healthz"}:
                _json_response(
                    self,
                    status=HTTPStatus.OK,
                    payload={"status": "ok", "service": "simple-mcp-template"},
                )
                return
            _text_response(self, status=HTTPStatus.NOT_FOUND, text="Not Found")

        def do_POST(self) -> None:  # noqa: N802
            path = (urlparse(self.path).path or "").strip()
            if path != normalized_mcp_path:
                _text_response(self, status=HTTPStatus.NOT_FOUND, text="Not Found")
                return

            if not _is_authorized(self.headers, expected_token=expected_token):
                _json_response(
                    self,
                    status=HTTPStatus.UNAUTHORIZED,
                    payload={
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32001, "message": "Unauthorized"},
                    },
                )
                return

            content_length = self.headers.get("Content-Length")
            if content_length is None:
                _json_response(
                    self,
                    status=HTTPStatus.BAD_REQUEST,
                    payload={
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": "Missing Content-Length"},
                    },
                )
                return

            try:
                length = int(content_length)
                body = json.loads(self.rfile.read(max(length, 0)).decode("utf-8"))
            except Exception:
                _json_response(
                    self,
                    status=HTTPStatus.BAD_REQUEST,
                    payload={
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": "Invalid JSON body"},
                    },
                )
                return

            if isinstance(body, list):
                responses: list[dict[str, object]] = []
                for item in body:
                    if not isinstance(item, dict):
                        responses.append(
                            {
                                "jsonrpc": "2.0",
                                "id": None,
                                "error": {
                                    "code": -32600,
                                    "message": "Invalid Request",
                                },
                            }
                        )
                        continue

                    response = handle_jsonrpc_message(item)
                    if response is not None:
                        responses.append(response)

                if not responses:
                    self.send_response(HTTPStatus.NO_CONTENT.value)
                    self.end_headers()
                    return
                _json_response(self, status=HTTPStatus.OK, payload=responses)
                return

            if not isinstance(body, dict):
                _json_response(
                    self,
                    status=HTTPStatus.BAD_REQUEST,
                    payload={
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32600, "message": "Invalid Request"},
                    },
                )
                return

            response = handle_jsonrpc_message(body)
            if response is None:
                self.send_response(HTTPStatus.NO_CONTENT.value)
                self.end_headers()
                return

            _json_response(self, status=HTTPStatus.OK, payload=response)

    return SimpleMCPHttpHandler


def run_http_server() -> None:
    host = str(os.getenv("SIMPLE_MCP_HOST", DEFAULT_HOST) or DEFAULT_HOST).strip()
    port_raw = str(os.getenv("SIMPLE_MCP_PORT", str(DEFAULT_PORT)) or str(DEFAULT_PORT))
    mcp_path = _normalize_path(str(os.getenv("SIMPLE_MCP_PATH", DEFAULT_PATH) or DEFAULT_PATH))
    expected_token = str(os.getenv("SIMPLE_MCP_TOKEN", "") or "").strip()

    try:
        port = int(port_raw)
    except Exception:
        port = DEFAULT_PORT

    handler = create_handler(mcp_path=mcp_path, expected_token=expected_token)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Simple MCP server listening on http://{host}:{port}{mcp_path}")
    server.serve_forever()


if __name__ == "__main__":
    run_http_server()
