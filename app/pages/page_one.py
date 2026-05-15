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
default_indicator = "gdp_per_capita_current_usd"
default_indicator_index = (
    indicator_options.index(default_indicator)
    if default_indicator in indicator_options
    else 0
)
countries = sorted(data["country_name"].dropna().unique())
default_countries = [
    country for country in ["United States", "China", "India"] if country in countries
]
min_year = int(data["year"].min())
max_year = int(data["year"].max())

st.title("World Bank Development Indicators")

st.subheader(" This is me")

with st.sidebar:
    st.header("Filters")
    st.write("hello")
    selected_indicator = st.selectbox(
        "Indicator",
        options=indicator_options,
        index=default_indicator_index,
        format_func=lambda slug: indicator_labels[slug],
    )
    selected_countries = st.multiselect(
        "Countries",
        options=countries,
        default=default_countries,
    )
    year_range = st.slider(
        "Years",
        min_value=min_year,
        max_value=max_year,
        value=(2000, max_year),
    )
    display_mode = st.radio(
        "Display",
        options=["Levels", "Percent change"],
        horizontal=True,
    )

filtered = data[
    (data["indicator_slug"] == selected_indicator)
    & (data["country_name"].isin(selected_countries))
].sort_values(["country_name", "year"])

if display_mode == "Percent change":
    filtered["value"] = filtered.groupby("country_name")["value"].pct_change() * 100
    filtered = filtered.dropna(subset=["value"])
    y_label = f"{indicator_labels[selected_indicator]} (% change)"
else:
    y_label = indicator_labels[selected_indicator]

filtered = filtered[filtered["year"].between(year_range[0], year_range[1])]

if selected_countries and not filtered.empty:
    st.line_chart(
        filtered,
        x="year",
        y="value",
        color="country_name",
        x_label="Year",
        y_label=y_label,
        height=480,
    )
else:
    st.info("Choose at least one country with available data.")
