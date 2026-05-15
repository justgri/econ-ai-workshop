import csv
from pathlib import Path

import streamlit as st


RAW_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def load_raw_data_columns():
    datasets = []

    for csv_path in sorted(RAW_DATA_DIR.glob("*.csv")):
        with csv_path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            columns = next(reader, [])

        datasets.append(
            {
                "file": csv_path.name,
                "column_count": len(columns),
                "columns": columns,
            }
        )

    return datasets


st.title("Raw Data Columns")
st.write("Column names from CSV files in `app/data/raw`, without displaying raw rows.")

datasets = load_raw_data_columns()

if not datasets:
    st.info("No CSV files found in `app/data/raw`.")
    st.stop()

file_names = [dataset["file"] for dataset in datasets]
selected_file = st.selectbox("Raw data file", file_names)
selected_dataset = next(dataset for dataset in datasets if dataset["file"] == selected_file)

st.metric("Columns", selected_dataset["column_count"])

st.dataframe(
    [{"Column": column} for column in selected_dataset["columns"]],
    use_container_width=True,
    hide_index=True,
)

with st.expander("All raw data files"):
    st.dataframe(
        [
            {
                "File": dataset["file"],
                "Column count": dataset["column_count"],
                "Columns": ", ".join(dataset["columns"]),
            }
            for dataset in datasets
        ],
        use_container_width=True,
        hide_index=True,
    )
