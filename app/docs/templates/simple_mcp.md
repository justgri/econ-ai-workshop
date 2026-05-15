# Simple MCP Template

`app/src/templates/simple_mcp/` is a neutral reference for showing local tools,
OpenAI function calling, and a tiny MCP-compatible server.

## Files Reviewed

| File | Role |
| --- | --- |
| `__init__.py` | Marks the folder as a package and describes the template. |
| `tools.py` | Defines the demo tools and their schemas. |
| `chat_runtime.py` | Runs an OpenAI chat turn with local function tools. |
| `mcp_server.py` | Exposes the same tools through a minimal JSON-RPC MCP stdio server. |
| `http_server.py` | Wraps the MCP handler in a small local HTTP server. |

## `tools.py`

This is the best starting point for live coding. It contains:

- `DEMO_NOTES`: tiny in-memory placeholder context.
- `get_tool_definitions()`: schemas that can be reused for OpenAI tools and MCP
  tools.
- `lookup_demo_note(query, limit=3)`: a simple searchable lookup.
- `calculate_percent_change(start_value, end_value)`: a small calculation tool.
- `call_tool(name, arguments=None)`: a dispatcher for the tool runtime.

To adapt it, replace `DEMO_NOTES` and add one or two clear functions that match
the demo data. Keep function inputs explicit and outputs JSON-serializable.

## `chat_runtime.py`

This file shows how to let an assistant call local Python functions:

- builds OpenAI tool definitions from `tools.py`
- starts a Responses API call
- extracts function calls from the response
- dispatches them through `demo_tools.call_tool(...)`
- sends function outputs back to the model
- returns assistant text, response id, trace, tool-round count, and model name

Useful functions and constants:

- `DEFAULT_MODEL`
- `DEFAULT_REASONING_EFFORT`
- `SYSTEM_INSTRUCTIONS`
- `make_message(...)`
- `append_message(...)`
- `load_openai_api_key(...)`
- `run_chat_turn(...)`

This file is useful when the live demo needs a visible "model calls a tool,
tool returns data, model summarizes result" moment.

## `mcp_server.py`

This file is a minimal MCP-style stdio server. It supports:

- `initialize`
- `notifications/initialized`
- `ping`
- `tools/list`
- `tools/call`

It reads and writes content-length framed JSON-RPC messages on stdio. The server
does not add external dependencies, databases, authentication, or background
jobs. It is designed as a readable protocol reference.

## `http_server.py`

This file exposes the same JSON-RPC handler over local HTTP:

- default host: `127.0.0.1`
- default port: `8765`
- default MCP path: `/mcp`
- health endpoints: `/health` and `/healthz`
- optional bearer-token check via `SIMPLE_MCP_TOKEN`

Use this only if HTTP is easier to demonstrate than stdio. For a short live
coding segment, `tools.py` plus `chat_runtime.py` is usually enough.

## Dependencies

The local tools and servers use the Python standard library. `chat_runtime.py`
also needs `openai` when calling the model.

## Good Live Demo Edits

- Replace `lookup_demo_note` with a lookup over the workshop dataset.
- Replace `calculate_percent_change` with one economics calculation that is easy
  to verify on screen.
- Keep `call_tool` as the single dispatcher so the tool list stays easy to
  explain.
- Show `tool_trace` in Streamlit if the audience should see what was called.
