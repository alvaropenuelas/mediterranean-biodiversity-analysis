import requests
import pandas as pd
from pathlib import Path

OBIS_API = "https://api.obis.org/v3/occurrence"
MED_POLYGON = "POLYGON((-6 30, 36 30, 36 46, -6 46, -6 30))"


def fetch_mediterranean_species(output_path="data/raw/obis_mediterranean.csv"):
    params = {
        "geometry": MED_POLYGON,
        "startdate": "2000-01-01",
        "enddate": "2024-12-31",
        "size": 5000,
    }

    try:
        response = requests.get(OBIS_API, params=params, timeout=120)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"OBIS API request failed: {exc}") from exc

    records = response.json().get("results", [])
    if len(records) == params["size"]:
        print(f"WARNING: returned record count equals page size ({params['size']}); dataset may be truncated.")
    df = pd.DataFrame(records)

    if df.empty:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print("No records returned from OBIS API")
        return df

    keep = [c for c in ["decimalLongitude", "decimalLatitude", "species", "year", "depth", "class"]
            if c in df.columns]
    df = df[keep].copy()
    df = df.dropna(subset=["decimalLongitude", "decimalLatitude", "species"])

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} records → {output_path}")
    return df
