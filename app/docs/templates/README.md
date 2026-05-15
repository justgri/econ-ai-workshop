# Template Reference

This folder documents the small helper templates in `app/src/templates/`.
They are intentionally lightweight references for the live Econ + AI workshop
demo, not production-ready packages.

## Template Set

| Template | Files | Use It For |
| --- | --- | --- |
| `simple_chat` | `chat_constants.py`, `utils_chat.py`, `streamlit_app.py` | A minimal Streamlit chat app and reusable OpenAI chat helpers. |
| `simple_mcp` | `__init__.py`, `tools.py`, `chat_runtime.py`, `mcp_server.py`, `http_server.py` | A neutral local tool-calling and MCP reference. |
| `simple_transcribe` | `transcribe.py` | Small Whisper transcript chunking helpers for audio or video demos. |

## What Was Reviewed

The current template tree contains only generic helper code:

- `app/src/templates/simple_chat/chat_constants.py`
- `app/src/templates/simple_chat/utils_chat.py`
- `app/src/templates/simple_chat/streamlit_app.py`
- `app/src/templates/simple_mcp/__init__.py`
- `app/src/templates/simple_mcp/tools.py`
- `app/src/templates/simple_mcp/chat_runtime.py`
- `app/src/templates/simple_mcp/mcp_server.py`
- `app/src/templates/simple_mcp/http_server.py`
- `app/src/templates/simple_transcribe/transcribe.py`

No old paper replication files, generated artifacts, cache directories, or
project-specific course assistant prompts remain in `app/src/templates/`.

## How To Use These Templates

Copy only the function or file you need into the live demo. Keep the copied
version small enough to explain while coding.

Prefer this order during the workshop:

1. Start with native Streamlit state and widgets.
2. Add `simple_chat` helpers when the demo needs a chat turn.
3. Add `simple_mcp` helpers only when showing tool calls or MCP.
4. Add `simple_transcribe` helpers only if the demo needs timed transcript
   chunks.

## Documentation Pages

- [Simple Chat](simple_chat.md)
- [Simple MCP](simple_mcp.md)
- [Simple Transcribe](simple_transcribe.md)
