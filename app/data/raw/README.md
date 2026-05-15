# World Bank WDI Demo Data

This folder contains small, workshop-friendly downloads from the World Bank
Indicators API.

Files:

- `worldbank_wdi_simple_long.csv`: one row per country/economy, year, and indicator.
- `worldbank_wdi_simple_wide.csv`: one row per country/economy and year, with indicators as columns.
- `worldbank_countries.csv`: country/economy metadata from the World Bank API.
- `worldbank_wdi_simple_metadata.json`: download timestamp, API source, indicator list, and row counts.

Indicators:

- `NY.GDP.MKTP.CD`: GDP (current US$)
- `NY.GDP.MKTP.KD.ZG`: GDP growth (annual %)
- `NY.GDP.PCAP.CD`: GDP per capita (current US$)
- `SH.DYN.MORT`: Mortality rate, under-5 (per 1,000 live births)
- `SP.DYN.LE00.IN`: Life expectancy at birth, total (years)
- `SP.POP.TOTL`: Population, total

To refresh the data:

```bash
python3 app/src/scripts/download_worldbank_data.py
```
