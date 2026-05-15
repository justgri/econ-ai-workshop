from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def format_timestamp(seconds: float) -> str:
    """Format seconds as M:SS or H:MM:SS."""
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def chunk_transcript_segments(
    segments: list[dict[str, Any]],
    *,
    chunk_duration: int = 30,
) -> list[dict[str, Any]]:
    """Group Whisper-style transcript segments into simple timed chunks."""
    chunks: list[dict[str, Any]] = []
    current_text: list[str] = []
    chunk_start: float | None = None
    chunk_end = 0.0

    for segment in segments:
        start = float(segment.get("start", 0.0) or 0.0)
        end = float(segment.get("end", start) or start)
        text = str(segment.get("text", "") or "").strip()
        if not text:
            continue

        if chunk_start is None:
            chunk_start = start

        if current_text and end - chunk_start > chunk_duration:
            chunks.append(_make_chunk(chunk_start, chunk_end, current_text))
            current_text = []
            chunk_start = start

        current_text.append(text)
        chunk_end = end

    if current_text and chunk_start is not None:
        chunks.append(_make_chunk(chunk_start, chunk_end, current_text))

    return chunks


def _make_chunk(start: float, end: float, text_parts: list[str]) -> dict[str, Any]:
    return {
        "start_time": round(start, 2),
        "end_time": round(end, 2),
        "timestamp": format_timestamp(start),
        "time_range": f"{format_timestamp(start)} - {format_timestamp(end)}",
        "text": " ".join(text_parts),
    }


def transcribe_media(
    media_path: str | Path,
    *,
    model_size: str = "base",
    language: str | None = None,
    chunk_duration: int = 30,
) -> list[dict[str, Any]]:
    """Transcribe one audio/video file with Whisper and return timed chunks."""
    try:
        import whisper
    except ImportError as exc:
        raise RuntimeError("Install openai-whisper to use this helper.") from exc

    model = whisper.load_model(model_size)
    result = model.transcribe(str(media_path), language=language)
    segments = result.get("segments", [])
    return chunk_transcript_segments(segments, chunk_duration=chunk_duration)


def save_chunks_json(chunks: list[dict[str, Any]], output_path: str | Path) -> None:
    """Save transcript chunks as JSON."""
    Path(output_path).write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save_chunks_markdown(chunks: list[dict[str, Any]], output_path: str | Path) -> None:
    """Save transcript chunks in a lightweight Markdown format."""
    blocks = []
    for index, chunk in enumerate(chunks, start=1):
        blocks.append(
            "\n".join(
                [
                    f"## Chunk {index}",
                    f"Time: {chunk['time_range']}",
                    "",
                    str(chunk["text"]),
                ]
            )
        )

    Path(output_path).write_text("\n\n".join(blocks), encoding="utf-8")
