from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any

try:
    from . import tools as demo_tools
except ImportError:  # Allows `python mcp_server.py` while live-coding.
    import tools as demo_tools  # type: ignore[no-redef]


JSONRPC_VERSION = "2.0"
MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "simple-mcp-template"
SERVER_VERSION = "0.1.0"


@dataclass(frozen=True)
class JsonRpcError:
    code: int
    message: str
    data: object | None = None

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {"code": self.code, "message": self.message}
        if self.data is not None:
            payload["data"] = self.data
        return payload


def _error_response(request_id: object, err: JsonRpcError) -> dict[str, object]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "error": err.as_dict()}


def _result_response(request_id: object, result: dict[str, object]) -> dict[str, object]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}


def _tool_defs_for_mcp() -> list[dict[str, object]]:
    return [
        {
            "name": definition["name"],
            "description": definition.get("description", ""),
            "inputSchema": definition.get("input_schema", {"type": "object"}),
        }
        for definition in demo_tools.get_tool_definitions()
    ]


def _build_text_tool_result(payload: dict[str, object]) -> dict[str, object]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, ensure_ascii=False),
            }
        ],
        "structuredContent": payload,
        "isError": payload.get("status") == "error",
    }


def _dispatch_tool(name: str, arguments: dict[str, Any]) -> dict[str, object]:
    return demo_tools.call_tool(name, arguments)


def handle_jsonrpc_message(message: dict[str, object]) -> dict[str, object] | None:
    request_id = message.get("id")
    method = str(message.get("method", "") or "")
    params = message.get("params", {})

    if not method:
        if request_id is None:
            return None
        return _error_response(
            request_id,
            JsonRpcError(code=-32600, message="Invalid Request: missing method"),
        )

    if method == "initialize":
        if request_id is None:
            return None
        return _result_response(
            request_id,
            {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )

    if method == "notifications/initialized":
        return None

    if method == "ping":
        if request_id is None:
            return None
        return _result_response(request_id, {})

    if method == "tools/list":
        if request_id is None:
            return None
        return _result_response(request_id, {"tools": _tool_defs_for_mcp()})

    if method == "tools/call":
        if request_id is None:
            return None
        try:
            if not isinstance(params, dict):
                raise ValueError("params must be an object")
            name = str(params.get("name", "") or "").strip()
            arguments = params.get("arguments", {})
            if not name:
                raise ValueError("Missing required params.name")
            if arguments is None:
                arguments = {}
            if not isinstance(arguments, dict):
                raise ValueError("params.arguments must be an object")

            payload = _dispatch_tool(name, arguments)
            return _result_response(request_id, _build_text_tool_result(payload))
        except Exception as exc:
            return _error_response(
                request_id,
                JsonRpcError(code=-32000, message="Tool execution error", data=str(exc)),
            )

    if request_id is None:
        return None
    return _error_response(
        request_id,
        JsonRpcError(code=-32601, message=f"Method not found: {method}"),
    )


def _read_one_message(stream) -> dict[str, object] | None:
    content_length: int | None = None

    while True:
        header_line = stream.readline()
        if not header_line:
            return None
        if header_line in (b"\r\n", b"\n"):
            break

        line = header_line.decode("utf-8", errors="replace").strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.lower().strip() == "content-length":
            content_length = int(value.strip())

    if content_length is None or content_length < 0:
        return None

    payload = stream.read(content_length)
    if not payload:
        return None
    return json.loads(payload.decode("utf-8"))


def _write_one_message(stream, message: dict[str, object]) -> None:
    payload = json.dumps(message, ensure_ascii=False).encode("utf-8")
    stream.write(f"Content-Length: {len(payload)}\r\n\r\n".encode("ascii"))
    stream.write(payload)
    stream.flush()


def run_stdio_server() -> None:
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer

    while True:
        request = _read_one_message(stdin)
        if request is None:
            break
        response = handle_jsonrpc_message(request)
        if response is not None:
            _write_one_message(stdout, response)


if __name__ == "__main__":
    run_stdio_server()
