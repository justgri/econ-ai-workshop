# Simple Chat Template

`app/src/templates/simple_chat/` is a compact reference for adding a chat
interface to the live Streamlit demo.

## Files Reviewed

| File | Role |
| --- | --- |
| `chat_constants.py` | Keeps the default model, history length, system prompt, and tiny demo context in one easy-to-edit place. |
| `utils_chat.py` | Provides reusable message, history, prompt, API key, streaming, and non-streaming response helpers. |
| `streamlit_app.py` | Shows the smallest complete Streamlit chat app using the helpers. |

## `chat_constants.py`

This file is intentionally just configuration:

- `DEFAULT_MODEL`: the model used by the reference app.
- `MAX_HISTORY_MESSAGES`: how many recent chat messages to send.
- `DEFAULT_SYSTEM_PROMPT`: the baseline assistant behavior.
- `DEMO_CONTEXT`: a few placeholder context items that can be replaced during
  the live demo.

Replace `DEMO_CONTEXT` with workshop data, chart summaries, table summaries, or
other local context. Keep each item short so the prompt remains easy to explain.

## `utils_chat.py`

This file contains the reusable pieces:

- `make_message(role, content)`: creates a Streamlit/OpenAI-style message dict.
- `append_message(history, role=..., content=...)`: appends one message to an
  existing history list.
- `trim_history(history, max_messages=...)`: keeps recent `user` and
  `assistant` messages only.
- `load_openai_api_key(secrets=None)`: reads `OPENAI_API_KEY` from the
  environment first, then from a caller-provided mapping.
- `build_context_block(context_items)`: formats short local context items.
- `build_instructions(...)`: combines the system prompt and optional context.
- `build_input_messages(...)`: turns user input and history into model input.
- `stream_chat_response(...)`: streams text from the OpenAI Responses API.
- `complete_chat_response(...)`: convenience wrapper when streaming is not
  needed.

The most useful live-coding pattern is:

```python
history_before_turn = list(st.session_state.messages)
append_message(st.session_state.messages, role="user", content=user_message)
response = st.write_stream(
    stream_chat_response(
        user_message,
        api_key=api_key,
        history=history_before_turn,
        context_items=DEMO_CONTEXT,
    )
)
append_message(st.session_state.messages, role="assistant", content=response)
```

## `streamlit_app.py`

This is the full reference app:

- initializes `st.session_state.messages`
- displays previous chat messages
- collects a new prompt with `st.chat_input`
- streams the assistant answer into `st.chat_message("assistant")`
- offers a sidebar model text input and context toggle
- includes a clear-chat button

Use it as a scaffold when you want the audience to see the whole chat loop in
one file. For the main workshop app, it is often better to copy only the helper
functions you need.

## Dependencies

The template expects:

- `streamlit` for the reference app
- `openai` for API calls
- `OPENAI_API_KEY` available in the environment, or passed indirectly through a
  mapping in code

The current workshop `app/requirements.txt` only lists `streamlit`, so add
`openai` only if the live demo will call the API from this template.

## Good Live Demo Edits

- Change `DEFAULT_SYSTEM_PROMPT` to match the demo persona.
- Replace `DEMO_CONTEXT` with a tiny list derived from local demo data.
- Reduce `MAX_HISTORY_MESSAGES` if the prompt should be very small.
- Remove the sidebar model input if the live app should stay visually simple.
