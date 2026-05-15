import streamlit as st

st.set_page_config(
    page_title="Econ + AI Workshop Demo",
    layout="wide",
)

pages = [
    st.Page("pages/page_one.py", title="World Bank Data", icon=":material/show_chart:"),
    st.Page("pages/page_two.py", title="Page Two", icon=":material/filter_2:"),
    st.Page(
        "pages/raw_data_columns.py",
        title="Raw Data Columns",
        icon=":material/table_chart:",
    ),
]

page = st.navigation(pages, position="sidebar")

with st.sidebar:
    # Add shared sidebar controls here.
    pass

page.run()
