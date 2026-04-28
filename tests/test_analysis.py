import pytest
import pandas as pd
from src.analysis import load_and_merge


def test_merge_produces_richness_column(tmp_path):
    obis_data = pd.DataFrame({
        "decimalLongitude": [15.1, 15.3, 20.1],
        "decimalLatitude": [38.1, 38.2, 35.0],
        "species": ["Mullus surmuletus", "Octopus vulgaris", "Mullus surmuletus"],
        "year": [2020, 2021, 2022],
    })
    env_data = pd.DataFrame({
        "lon": [15.0, 20.0],
        "lat": [38.0, 35.0],
        "cell_key": ["38.0_15.0", "35.0_20.0"],
        "sst_c": [22.0, 24.0],
        "ph": [8.10, 8.05],
        "salinity_psu": [37.5, 38.0],
        "mean_depth_m": [80.0, 60.0],
    })

    obis_path = str(tmp_path / "obis.csv")
    env_path = str(tmp_path / "env.csv")
    processed_path = str(tmp_path / "merged.csv")

    obis_data.to_csv(obis_path, index=False)
    env_data.to_csv(env_path, index=False)

    merged, _ = load_and_merge(
        obis_path=obis_path,
        env_path=env_path,
        processed_path=processed_path,
    )

    assert "species_richness" in merged.columns
    assert len(merged) > 0
    assert (tmp_path / "merged.csv").exists()
