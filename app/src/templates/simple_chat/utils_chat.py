from __future__ import annotations

import os
from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import Any

try:
    from .chat_constants import (
        DEFAULT_MODEL,
        DEFAULT_SYSTEM_PROMPT,
        MAX_HISTORY_MESSAGES,
    )
except ImportError:  # Allows `python utils_chat.py` while live-coding.
    from chat_constants import (  # type: ignore[no-redef]
        DEFAULT_MODEL,
        DEFAULT_SYSTEM_PROMPT,
        MAX_HISTORY_MESSAGES,
    )


Message = dict[str, str]


def make_message(role: str, content: str) -> Message:
    """Create the small message dict used by Streamlit chat widgets."""
    return {"role": str(role), "content": str(content)}


def append_message(history: list[Message], *, role: str, content: str) -> list[Message]:
    """Append one message and return the same list for convenient assignment."""
    history.append(make_message(role, content))
    return history


def trim_history(
    history: Sequence[Mapping[str, Any]],
    *,
    max_messages: int = MAX_HISTORY_MESSAGES,
) -> list[Message]:
    """Keep the most recent chat turns in a clean OpenAI-compatible shape."""
    clean_messages: list[Message] = []
    for message in history[-max_messages:]:
        role = str(message.get("role", "") or "")
        content = str(message.get("content", "") or "")
        if role in {"user", "assistant"} and content:
            clean_messages.append(make_message(role, content))
    return clean_messages


def _mapping_get(source: object, key: str) -> Any:
    if isinstance(source, Mapping):
        return source.get(key)
    getter = getattr(source, "get", None)
    if callable(getter):
        return getter(key)
    return None


def _secret_candidates(secrets: object | None) -> Iterable[Any]:
    if secrets is None:
        return []

    direct_keys = [
        "OPENAI_API_KEY",
        "openai_api_key",
    ]
    nested_keys = [
        ("openai", "api_key"),
        ("chat", "OPENAI_API_KEY"),
    ]

    candidates: list[Any] = [_mapping_get(secrets, key) for key in direct_keys]
    for block_name, key in nested_keys:
        block = _mapping_get(secrets, block_name)
        candidates.append(_mapping_get(block, key))
    return candidates


def load_openai_api_key(*, secrets: object | None = None) -> str:
    """Load an API key from the environment or a caller-provided mapping."""
    env_key = str(os.getenv("OPENAI_API_KEY", "") or "").strip()
    if env_key:
        return env_key

    for candidate in _secret_candidates(secrets):
        if candidate:
            return str(candidate).strip()

    raise RuntimeError(
        "OpenAI API key not found. Set OPENAI_API_KEY or pass a secrets mapping "
        "with OPENAI_API_KEY, openai.api_key, or chat.OPENAI_API_KEY."
    )


def build_context_block(
    context_items: Sequence[Mapping[str, Any]] | None,
    *,
    title: str = "Demo context",
) -> str:
    """Format a short list of local context items for a chat prompt."""
    if not context_items:
        return ""

    lines = [title]
    for index, item in enumerate(context_items, start=1):
        label = str(item.get("title") or item.get("topic") or f"Item {index}")
        text = str(item.get("text") or item.get("content") or "").strip()
        if text:
            lines.append(f"- {label}: {text}")

    return "\n".join(lines)


def build_instructions(
    *,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    context_items: Sequence[Mapping[str, Any]] | None = None,
) -> str:
    """Combine base instructions with optional local context."""
    context_block = build_context_block(context_items)
    if not context_block:
        return system_prompt
    return f"{system_prompt}\n\nUse this local context when relevant:\n{context_block}"


def build_input_messages(
    user_message: str,
    *,
    history: Sequence[Mapping[str, Any]] | None = None,
    max_messages: int = MAX_HISTORY_MESSAGES,
) -> list[Message]:
    """Create the message list sent as Responses API input."""
    messages = trim_history(history or [], max_messages=max_messages)
    messages.append(make_message("user", user_message))
    return messages


def stream_chat_response(
    user_message: str,
    *,
    api_key: str,
    history: Sequence[Mapping[str, Any]] | None = None,
    context_items: Sequence[Mapping[str, Any]] | None = None,
    model: str = DEFAULT_MODEL,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
) -> Iterator[str]:
    """Yield text chunks for one OpenAI Responses API chat turn."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    instructions = build_instructions(
        system_prompt=system_prompt,
        context_items=context_items,
    )
    input_messages = build_input_messages(user_message, history=history)

    with client.responses.stream(
        model=model,
        instructions=instructions,
        input=input_messages,
        text={"verbosity": "low"},
    ) as stream:
        for event in stream:
            if event.type == "response.output_text.delta" and event.delta:
                yield event.delta


def complete_chat_response(
    user_message: str,
    *,
    api_key: str,
    history: Sequence[Mapping[str, Any]] | None = None,
    context_items: Sequence[Mapping[str, Any]] | None = None,
    model: str = DEFAULT_MODEL,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
) -> str:
    """Return a full response string when streaming is not needed."""
    return "".join(
        stream_chat_response(
            user_message,
            api_key=api_key,
            history=history,
            context_items=context_items,
            model=model,
            system_prompt=system_prompt,
        )
    )
