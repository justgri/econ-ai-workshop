import streamlit as st

st.set_page_config(
    page_title="Econ + AI Workshop Demo",
    layout="wide",
)

pages = [
    st.Page("pages/page_one.py", title="Page One", icon=":material/filter_1:"),
    st.Page("pages/page_two.py", title="Page Two", icon=":material/filter_2:"),
]

page = st.navigation(pages, position="sidebar")

with st.sidebar:
    # Add shared sidebar controls here.
    pass

page.run()
