from __future__ import annotations

import streamlit as st

try:
    from .chat_constants import DEFAULT_MODEL, DEMO_CONTEXT
    from .utils_chat import append_message, load_openai_api_key, stream_chat_response
except ImportError:  # Allows `streamlit run streamlit_app.py` from this folder.
    from chat_constants import DEFAULT_MODEL, DEMO_CONTEXT  # type: ignore[no-redef]
    from utils_chat import (  # type: ignore[no-redef]
        append_message,
        load_openai_api_key,
        stream_chat_response,
    )


st.set_page_config(page_title="Simple Chat Template", layout="centered")

st.title("Simple Chat Template")
st.caption("Small reference app for the Econ + AI live demo.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    model = st.text_input("Model", value=DEFAULT_MODEL)
    use_demo_context = st.toggle("Use demo context", value=True)

    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_message = st.chat_input("Ask about the workshop demo...")
if not user_message:
    st.stop()

with st.chat_message("user"):
    st.markdown(user_message)

history_before_turn = list(st.session_state.messages)
append_message(st.session_state.messages, role="user", content=user_message)

try:
    api_key = load_openai_api_key()
except RuntimeError as exc:
    with st.chat_message("assistant"):
        st.warning(str(exc))
    st.stop()

context_items = DEMO_CONTEXT if use_demo_context else None

with st.chat_message("assistant"):
    response = st.write_stream(
        stream_chat_response(
            user_message,
            api_key=api_key,
            history=history_before_turn,
            context_items=context_items,
            model=model,
        )
    )

append_message(st.session_state.messages, role="assistant", content=response)
