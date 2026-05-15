"""Download a small World Bank WDI panel for the workshop demo.

The script uses only the Python standard library so it is easy to explain and
rerun during a live coding session.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_BASE = "https://api.worldbank.org/v2"
DEFAULT_START_YEAR = 1960
DEFAULT_END_YEAR = 2024

INDICATORS = [
    {
        "code": "NY.GDP.MKTP.CD",
        "slug": "gdp_current_usd",
        "label": "GDP (current US$)",
    },
    {
        "code": "NY.GDP.MKTP.KD.ZG",
        "slug": "gdp_growth_annual_pct",
        "label": "GDP growth (annual %)",
    },
    {
        "code": "NY.GDP.PCAP.CD",
        "slug": "gdp_per_capita_current_usd",
        "label": "GDP per capita (current US$)",
    },
    {
        "code": "SH.DYN.MORT",
        "slug": "under5_mortality_per_1000",
        "label": "Mortality rate, under-5 (per 1,000 live births)",
    },
    {
        "code": "SP.DYN.LE00.IN",
        "slug": "life_expectancy_years",
        "label": "Life expectancy at birth, total (years)",
    },
    {
        "code": "SP.POP.TOTL",
        "slug": "population_total",
        "label": "Population, total",
    },
]

LONG_FIELDS = [
    "country_id",
    "country_code",
    "country_name",
    "region",
    "income_level",
    "is_country",
    "year",
    "indicator_code",
    "indicator_slug",
    "indicator_name",
    "value",
    "unit",
    "obs_status",
    "decimal",
]

COUNTRY_FIELDS = [
    "country_code",
    "iso2_code",
    "country_name",
    "region",
    "income_level",
    "lending_type",
    "capital_city",
    "longitude",
    "latitude",
    "is_country",
]


def fetch_json(url: str, retries: int = 3) -> object:
    request = Request(url, headers={"User-Agent": "econ-ai-workshop/1.0"})
    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError) as error:
            if attempt == retries:
                raise RuntimeError(f"Could not fetch {url}") from error
            sleep(1.5 * attempt)
    raise RuntimeError(f"Could not fetch {url}")


def paged_world_bank_call(path: str, params: dict[str, str | int]) -> tuple[list[dict], list[dict]]:
    page = 1
    rows: list[dict] = []
    metadata: list[dict] = []

    while True:
        query = params | {"format": "json", "per_page": 20000, "page": page}
        url = f"{API_BASE}/{path}?{urlencode(query)}"
        payload = fetch_json(url)

        if not isinstance(payload, list) or len(payload) < 2:
            raise RuntimeError(f"Unexpected World Bank response for {url}")

        page_metadata, page_rows = payload[0], payload[1] or []
        metadata.append(page_metadata)
        rows.extend(page_rows)

        if page >= int(page_metadata.get("pages", 1)):
            return metadata, rows

        page += 1


def value_from_nested(row: dict, key: str) -> str:
    value = row.get(key, {})
    if isinstance(value, dict):
        return str(value.get("value") or "")
    return ""


def optional_string(value: object) -> str:
    return "" if value is None else str(value)


def fetch_country_metadata() -> tuple[dict[str, dict[str, str]], list[dict[str, str]]]:
    _, countries = paged_world_bank_call("country", {})
    country_lookup: dict[str, dict[str, str]] = {}
    country_rows: list[dict[str, str]] = []

    for country in countries:
        region_id = country.get("region", {}).get("id", "")
        country_code = str(country.get("id") or "")
        row = {
            "country_code": country_code,
            "iso2_code": optional_string(country.get("iso2Code")),
            "country_name": optional_string(country.get("name")),
            "region": value_from_nested(country, "region"),
            "income_level": value_from_nested(country, "incomeLevel"),
            "lending_type": value_from_nested(country, "lendingType"),
            "capital_city": optional_string(country.get("capitalCity")),
            "longitude": optional_string(country.get("longitude")),
            "latitude": optional_string(country.get("latitude")),
            "is_country": str(bool(region_id and region_id != "NA")),
        }
        country_lookup[country_code] = row
        country_rows.append(row)

    return country_lookup, country_rows


def normalize_indicator_row(
    row: dict,
    indicator: dict[str, str],
    country_lookup: dict[str, dict[str, str]],
) -> dict[str, str]:
    country_code = str(row.get("countryiso3code") or "")
    country = row.get("country", {})
    country_info = country_lookup.get(country_code, {})
    value = row.get("value")

    return {
        "country_id": optional_string(country.get("id")),
        "country_code": country_code,
        "country_name": optional_string(country.get("value")),
        "region": country_info.get("region", ""),
        "income_level": country_info.get("income_level", ""),
        "is_country": country_info.get("is_country", ""),
        "year": optional_string(row.get("date")),
        "indicator_code": indicator["code"],
        "indicator_slug": indicator["slug"],
        "indicator_name": optional_string(row.get("indicator", {}).get("value"))
        or indicator["label"],
        "value": optional_string(value),
        "unit": optional_string(row.get("unit")),
        "obs_status": optional_string(row.get("obs_status")),
        "decimal": optional_string(row.get("decimal")),
    }


def fetch_indicator_rows(
    indicator: dict[str, str],
    country_lookup: dict[str, dict[str, str]],
    start_year: int,
    end_year: int,
) -> tuple[list[dict[str, str]], list[dict]]:
    metadata, rows = paged_world_bank_call(
        f"country/all/indicator/{indicator['code']}",
        {
            "source": 2,
            "date": f"{start_year}:{end_year}",
        },
    )
    normalized = [normalize_indicator_row(row, indicator, country_lookup) for row in rows]
    return normalized, metadata


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def make_wide_rows(long_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    wide_lookup: dict[tuple[str, str, str, str], dict[str, str]] = {}
    value_columns = [indicator["slug"] for indicator in INDICATORS]

    for row in long_rows:
        key = (
            row["country_code"],
            row["country_id"],
            row["country_name"],
            row["year"],
        )
        if key not in wide_lookup:
            wide_lookup[key] = {
                "country_id": row["country_id"],
                "country_code": row["country_code"],
                "country_name": row["country_name"],
                "region": row["region"],
                "income_level": row["income_level"],
                "is_country": row["is_country"],
                "year": row["year"],
                **{column: "" for column in value_columns},
            }
        wide_lookup[key][row["indicator_slug"]] = row["value"]

    return sorted(
        wide_lookup.values(),
        key=lambda item: (item["country_code"], int(item["year"] or 0)),
    )


def parse_args() -> argparse.Namespace:
    app_dir = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=DEFAULT_START_YEAR)
    parser.add_argument("--end-year", type=int, default=DEFAULT_END_YEAR)
    parser.add_argument("--output-dir", type=Path, default=app_dir / "data" / "raw")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    country_lookup, country_rows = fetch_country_metadata()
    long_rows: list[dict[str, str]] = []
    api_metadata_by_indicator: dict[str, list[dict]] = {}

    for indicator in INDICATORS:
        rows, api_metadata = fetch_indicator_rows(
            indicator,
            country_lookup,
            args.start_year,
            args.end_year,
        )
        long_rows.extend(rows)
        api_metadata_by_indicator[indicator["code"]] = api_metadata

    long_rows = sorted(
        long_rows,
        key=lambda row: (
            row["indicator_code"],
            row["country_code"],
            int(row["year"] or 0),
        ),
    )
    wide_rows = make_wide_rows(long_rows)

    write_csv(args.output_dir / "worldbank_wdi_simple_long.csv", long_rows, LONG_FIELDS)
    write_csv(
        args.output_dir / "worldbank_wdi_simple_wide.csv",
        wide_rows,
        LONG_FIELDS[:7] + [indicator["slug"] for indicator in INDICATORS],
    )
    write_csv(args.output_dir / "worldbank_countries.csv", country_rows, COUNTRY_FIELDS)

    metadata = {
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "World Bank Indicators API",
        "source_docs_url": "https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation",
        "api_base_url": API_BASE,
        "date_range": f"{args.start_year}:{args.end_year}",
        "indicators": INDICATORS,
        "rows": {
            "long": len(long_rows),
            "wide": len(wide_rows),
            "countries": len(country_rows),
        },
        "api_metadata_by_indicator": api_metadata_by_indicator,
    }

    with (args.output_dir / "worldbank_wdi_simple_metadata.json").open(
        "w",
        encoding="utf-8",
    ) as metadata_file:
        json.dump(metadata, metadata_file, indent=2)
        metadata_file.write("\n")

    print(f"Wrote {len(long_rows):,} long rows and {len(wide_rows):,} wide rows")
    print(f"Output directory: {args.output_dir}")


if __name__ == "__main__":
    main()
