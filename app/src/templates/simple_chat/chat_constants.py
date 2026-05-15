DEFAULT_MODEL = "gpt-5-mini"
MAX_HISTORY_MESSAGES = 12

DEFAULT_SYSTEM_PROMPT = (
    "You are a concise assistant for a live Econ + AI workshop demo. "
    "Answer clearly, keep the tone friendly, and format responses for "
    "Streamlit chat."
)

DEMO_CONTEXT = [
    {
        "title": "Workshop goal",
        "text": "Show how a small Streamlit app can become an AI-assisted economics demo.",
    },
    {
        "title": "Useful pattern",
        "text": "Keep message history in session_state and send only the recent turns.",
    },
    {
        "title": "Demo data",
        "text": "Local, public, workshop-sized data is easier to explain live.",
    },
]
