# Simple Transcribe Template

`app/src/templates/simple_transcribe/transcribe.py` is a small reference for
turning audio or video transcripts into timed chunks.

## File Reviewed

| File | Role |
| --- | --- |
| `transcribe.py` | Formats timestamps, chunks Whisper-style transcript segments, optionally runs Whisper, and saves chunks. |

## Functions

- `format_timestamp(seconds)`: converts seconds into `M:SS` or `H:MM:SS`.
- `chunk_transcript_segments(segments, chunk_duration=30)`: groups
  Whisper-style segments into readable timed chunks.
- `transcribe_media(media_path, model_size="base", language=None, chunk_duration=30)`:
  loads Whisper, transcribes one media file, and returns chunks.
- `save_chunks_json(chunks, output_path)`: writes chunk dictionaries as JSON.
- `save_chunks_markdown(chunks, output_path)`: writes a readable Markdown
  transcript.

## Expected Segment Shape

`chunk_transcript_segments` expects a list of dictionaries like this:

```python
segments = [
    {"start": 0.0, "end": 4.2, "text": "Welcome to the demo."},
    {"start": 4.2, "end": 9.5, "text": "Now we load the data."},
]
```

It returns chunk dictionaries with:

- `start_time`
- `end_time`
- `timestamp`
- `time_range`
- `text`

## Dependencies

Chunking and saving use only the Python standard library. `transcribe_media`
requires `openai-whisper`, which is intentionally not part of the minimal
workshop dependencies unless transcription is part of the live demo.

## Good Live Demo Edits

- Skip `transcribe_media` and feed precomputed segments into
  `chunk_transcript_segments` if you want a fast, reliable workshop moment.
- Use `save_chunks_markdown` when the output should be readable by humans.
- Use `save_chunks_json` when the output will become local context for a chat
  assistant.
- Keep `chunk_duration` short when the assistant should cite narrow transcript
  ranges.
