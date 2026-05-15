from __future__ import annotations

from collections.abc import Mapping
import json
import os
from dataclasses import dataclass
from typing import Any

try:
    from . import tools as demo_tools
except ImportError:  # Allows `python chat_runtime.py` while live-coding.
    import tools as demo_tools  # type: ignore[no-redef]


DEFAULT_MODEL = "gpt-5-mini"
DEFAULT_REASONING_EFFORT = "low"
DEFAULT_MAX_TOOL_ROUNDS = 4

SYSTEM_INSTRUCTIONS = (
    "You are a concise assistant for a live Econ + AI workshop demo. "
    "Use tools when they help you look up demo context or calculate a result. "
    "Keep answers short, clear, and suitable for rendering inside Streamlit chat."
)


@dataclass(frozen=True)
class ToolCall:
    call_id: str
    name: str
    arguments: dict[str, Any]


def _get_attr(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _get_mapping_value(source: Any, key: str, default: Any = None) -> Any:
    if isinstance(source, Mapping):
        return source.get(key, default)
    return default


def make_message(role: str, content: str) -> dict[str, str]:
    """Small Streamlit-friendly chat message helper."""
    return {"role": role, "content": content}


def append_message(
    history: list[dict[str, str]],
    *,
    role: str,
    content: str,
) -> list[dict[str, str]]:
    """Append a message and return the same list for convenient assignment."""
    history.append(make_message(role, content))
    return history


def load_openai_api_key(*, secrets: dict[str, Any] | None = None) -> str:
    """Load an API key from the environment or a caller-provided secrets mapping."""
    env_key = str(os.getenv("OPENAI_API_KEY", "") or "").strip()
    if env_key:
        return env_key

    source = secrets or {}
    if isinstance(source, Mapping):
        candidates = [
            source.get("OPENAI_API_KEY"),
            source.get("openai_api_key"),
        ]

        openai_block = source.get("openai", {})
        candidates.append(_get_mapping_value(openai_block, "api_key"))

        chat_block = source.get("chat", {})
        candidates.append(_get_mapping_value(chat_block, "OPENAI_API_KEY"))

        for candidate in candidates:
            if candidate:
                return str(candidate)

    raise RuntimeError(
        "OpenAI API key not found. Set OPENAI_API_KEY or pass a secrets mapping "
        "with OPENAI_API_KEY, openai.api_key, or chat.OPENAI_API_KEY."
    )


def _build_openai_tools() -> list[dict[str, object]]:
    openai_tools: list[dict[str, object]] = []
    for definition in demo_tools.get_tool_definitions():
        openai_tools.append(
            {
                "type": "function",
                "name": definition["name"],
                "description": definition.get("description", ""),
                "parameters": definition.get("input_schema", {"type": "object"}),
                "strict": False,
            }
        )
    return openai_tools


def _parse_arguments(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    text = str(raw or "").strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _extract_tool_calls(response: Any) -> list[ToolCall]:
    calls: list[ToolCall] = []
    for item in _get_attr(response, "output", []) or []:
        if str(_get_attr(item, "type", "") or "") != "function_call":
            continue

        call_id = str(_get_attr(item, "call_id", "") or "")
        name = str(_get_attr(item, "name", "") or "")
        if not call_id or not name:
            continue

        calls.append(
            ToolCall(
                call_id=call_id,
                name=name,
                arguments=_parse_arguments(_get_attr(item, "arguments", {})),
            )
        )
    return calls


def _extract_response_text(response: Any) -> str:
    output_text = _get_attr(response, "output_text", None)
    if output_text:
        text = str(output_text).strip()
        if text:
            return text

    parts: list[str] = []
    for item in _get_attr(response, "output", []) or []:
        if str(_get_attr(item, "type", "") or "") != "message":
            continue
        for block in _get_attr(item, "content", []) or []:
            block_type = str(_get_attr(block, "type", "") or "")
            if block_type not in {"output_text", "text"}:
                continue
            text_obj = _get_attr(block, "text", "")
            text = text_obj if isinstance(text_obj, str) else _get_attr(text_obj, "value", "")
            if str(text).strip():
                parts.append(str(text).strip())

    return "\n\n".join(parts) if parts else "I could not produce a final answer."


def _tool_trace_entry(
    *,
    call: ToolCall,
    result: dict[str, object],
) -> dict[str, object]:
    return {
        "tool_name": call.name,
        "arguments": call.arguments,
        "status": result.get("status"),
        "result_preview": result,
    }


def run_chat_turn(
    *,
    user_message: str,
    api_key: str,
    previous_response_id: str | None = None,
    model: str = DEFAULT_MODEL,
    instructions: str = SYSTEM_INSTRUCTIONS,
    max_tool_rounds: int = DEFAULT_MAX_TOOL_ROUNDS,
) -> dict[str, object]:
    """Run one assistant turn with local demo function tools."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    openai_tools = _build_openai_tools()

    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=user_message,
        previous_response_id=previous_response_id or None,
        tools=openai_tools,
        reasoning={"effort": DEFAULT_REASONING_EFFORT},
        text={"verbosity": "low"},
    )

    trace: list[dict[str, object]] = []
    tool_round = 0
    while tool_round < max_tool_rounds:
        calls = _extract_tool_calls(response)
        if not calls:
            break

        tool_outputs: list[dict[str, object]] = []
        for call in calls:
            try:
                result = demo_tools.call_tool(call.name, call.arguments)
            except Exception as exc:
                result = {"status": "error", "error": str(exc)}

            trace.append(_tool_trace_entry(call=call, result=result))
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                }
            )

        response = client.responses.create(
            model=model,
            instructions=instructions,
            previous_response_id=str(_get_attr(response, "id", "") or ""),
            input=tool_outputs,
            tools=openai_tools,
            reasoning={"effort": DEFAULT_REASONING_EFFORT},
            text={"verbosity": "low"},
        )
        tool_round += 1

    return {
        "assistant_text": _extract_response_text(response),
        "response_id": str(_get_attr(response, "id", "") or ""),
        "tool_trace": trace,
        "tool_rounds": tool_round,
        "model": model,
    }
