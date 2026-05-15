from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "worldbank_wdi_simple_long.csv"
)


@st.cache_data
def load_world_bank_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH)
    data = data[data["is_country"].astype(str).str.lower() == "true"].copy()
    data["year"] = pd.to_numeric(data["year"], errors="coerce")
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    data = data.dropna(subset=["year", "value"])
    data["year"] = data["year"].astype(int)
    return data


data = load_world_bank_data()
indicator_labels = (
    data[["indicator_slug", "indicator_name"]]
    .drop_duplicates()
    .sort_values("indicator_name")
    .set_index("indicator_slug")["indicator_name"]
    .to_dict()
)
indicator_options = list(indicator_labels)
default_indicator = "population_total"
default_indicator_index = (
    indicator_options.index(default_indicator)
    if default_indicator in indicator_options
    else 0
)
years = sorted(data["year"].unique(), reverse=True)

st.title("World Bank Bar Chart")

with st.sidebar:
    st.header("Bar Chart Filters")
    selected_indicator = st.selectbox(
        "Indicator",
        options=indicator_options,
        index=default_indicator_index,
        format_func=lambda slug: indicator_labels[slug],
    )
    selected_year = st.selectbox("Year", options=years)
    country_count = st.slider("Countries", min_value=5, max_value=25, value=10)

filtered = data[
    (data["indicator_slug"] == selected_indicator)
    & (data["year"] == selected_year)
].copy()
filtered = filtered.nlargest(country_count, "value").sort_values("value")

if filtered.empty:
    st.info("No data available for this indicator and year.")
else:
    st.bar_chart(
        filtered,
        x="country_name",
        y="value",
        x_label="Country",
        y_label=indicator_labels[selected_indicator],
        horizontal=True,
        height=520,
    )
