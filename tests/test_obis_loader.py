import pytest
import requests
from unittest.mock import patch, MagicMock
import pandas as pd
from src.obis_loader import fetch_mediterranean_species

MOCK_RESULTS = [
    {"decimalLongitude": 15.0, "decimalLatitude": 38.0, "species": "Mullus surmuletus", "year": 2020, "depth": 50.0, "class": "Actinopterygii"},
    {"decimalLongitude": 20.0, "decimalLatitude": 35.0, "species": "Octopus vulgaris", "year": 2019, "depth": 30.0, "class": "Cephalopoda"},
    {"decimalLongitude": None, "decimalLatitude": 38.0, "species": "Unknown sp.", "year": 2021},
]


def _mock_get(results):
    m = MagicMock()
    m.json.return_value = {"results": results}
    m.raise_for_status = MagicMock()
    return m


def test_returns_dataframe(tmp_path):
    with patch("src.obis_loader.requests.get", return_value=_mock_get(MOCK_RESULTS)):
        df = fetch_mediterranean_species(output_path=str(tmp_path / "obis.csv"))
    assert isinstance(df, pd.DataFrame)


def test_drops_missing_coordinates(tmp_path):
    with patch("src.obis_loader.requests.get", return_value=_mock_get(MOCK_RESULTS)):
        df = fetch_mediterranean_species(output_path=str(tmp_path / "obis.csv"))
    assert len(df) == 2  # third record has None longitude — must be dropped


def test_required_columns_present(tmp_path):
    with patch("src.obis_loader.requests.get", return_value=_mock_get(MOCK_RESULTS)):
        df = fetch_mediterranean_species(output_path=str(tmp_path / "obis.csv"))
    for col in ["decimalLongitude", "decimalLatitude", "species"]:
        assert col in df.columns, f"Missing required column: {col}"


def test_saves_csv(tmp_path):
    out = tmp_path / "obis.csv"
    with patch("src.obis_loader.requests.get", return_value=_mock_get(MOCK_RESULTS)):
        fetch_mediterranean_species(output_path=str(out))
    assert out.exists()


def test_raises_on_http_error(tmp_path):
    error_mock = MagicMock()
    error_mock.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    with patch("src.obis_loader.requests.get", return_value=error_mock):
        with pytest.raises(RuntimeError, match="OBIS API request failed"):
            fetch_mediterranean_species(output_path=str(tmp_path / "obis.csv"))


def test_drops_missing_species(tmp_path):
    results_with_no_species = [
        {"decimalLongitude": 15.0, "decimalLatitude": 38.0, "species": "Mullus surmuletus", "year": 2020},
        {"decimalLongitude": 20.0, "decimalLatitude": 35.0, "species": None, "year": 2019},
    ]
    with patch("src.obis_loader.requests.get", return_value=_mock_get(results_with_no_species)):
        df = fetch_mediterranean_species(output_path=str(tmp_path / "obis.csv"))
    assert len(df) == 1
    assert df.iloc[0]["species"] == "Mullus surmuletus"
