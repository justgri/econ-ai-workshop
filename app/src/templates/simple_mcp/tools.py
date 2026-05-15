from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


DEMO_NOTES = [
    {
        "topic": "workshop",
        "text": "This is a tiny placeholder knowledge base for a live Econ + AI demo.",
    },
    {
        "topic": "streamlit",
        "text": "Streamlit chat demos usually need message history, user input, and one response function.",
    },
    {
        "topic": "economics",
        "text": "Tool calls are useful when the assistant should calculate or look something up before answering.",
    },
]


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _normalize_limit(value: Any, *, default: int, max_value: int) -> int:
    try:
        limit = int(value)
    except Exception:
        limit = default
    return max(1, min(limit, max_value))


def get_tool_definitions() -> list[dict[str, object]]:
    """Return OpenAI/MCP-compatible tool schemas for the demo helpers."""
    return [
        {
            "name": "lookup_demo_note",
            "description": "Search a tiny in-memory note list. Replace this with your own lookup.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Optional text to search for in the demo notes.",
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5,
                        "description": "Maximum number of notes to return.",
                    },
                },
                "additionalProperties": False,
            },
        },
        {
            "name": "calculate_percent_change",
            "description": "Calculate a percent change between two values.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "start_value": {"type": "number"},
                    "end_value": {"type": "number"},
                },
                "required": ["start_value", "end_value"],
                "additionalProperties": False,
            },
        },
    ]


def lookup_demo_note(query: str = "", *, limit: int = 3) -> dict[str, object]:
    """Return matching placeholder notes for the assistant to cite."""
    query_text = str(query or "").strip().lower()
    note_limit = _normalize_limit(limit, default=3, max_value=5)

    matches = []
    for note in DEMO_NOTES:
        haystack = f"{note['topic']} {note['text']}".lower()
        if not query_text or query_text in haystack:
            matches.append(note)

    return {
        "status": "ok",
        "generated_at_utc": _utc_now_iso(),
        "query": query,
        "notes": matches[:note_limit],
        "template_hint": "Replace DEMO_NOTES and lookup_demo_note with your live-demo data lookup.",
    }


def calculate_percent_change(start_value: float, end_value: float) -> dict[str, object]:
    """Calculate a percent change with a small guard for division by zero."""
    start = float(start_value)
    end = float(end_value)
    change = end - start

    if start == 0:
        return {
            "status": "error",
            "generated_at_utc": _utc_now_iso(),
            "error": "Cannot calculate percent change from a zero start value.",
            "start_value": start,
            "end_value": end,
        }

    return {
        "status": "ok",
        "generated_at_utc": _utc_now_iso(),
        "start_value": start,
        "end_value": end,
        "absolute_change": change,
        "percent_change": (change / start) * 100,
    }


def call_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, object]:
    """Dispatch one demo tool by name."""
    args = arguments or {}

    if name == "lookup_demo_note":
        return lookup_demo_note(
            query=str(args.get("query", "") or ""),
            limit=_normalize_limit(args.get("limit", 3), default=3, max_value=5),
        )

    if name == "calculate_percent_change":
        if "start_value" not in args:
            raise ValueError("Missing required argument: start_value")
        if "end_value" not in args:
            raise ValueError("Missing required argument: end_value")
        return calculate_percent_change(
            start_value=float(args["start_value"]),
            end_value=float(args["end_value"]),
        )

    raise ValueError(f"Unknown tool: {name}")
