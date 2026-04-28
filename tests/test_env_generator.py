import pytest
import pandas as pd
from src.env_generator import generate_env_grid


def test_returns_dataframe(tmp_path):
    df = generate_env_grid(output_path=str(tmp_path / "env.csv"), resolution=2.0)
    assert isinstance(df, pd.DataFrame)


def test_required_columns(tmp_path):
    df = generate_env_grid(output_path=str(tmp_path / "env.csv"), resolution=2.0)
    for col in ["lon", "lat", "cell_key", "sst_c", "ph", "salinity_psu", "mean_depth_m"]:
        assert col in df.columns, f"Missing column: {col}"


def test_sst_in_range(tmp_path):
    df = generate_env_grid(output_path=str(tmp_path / "env.csv"), resolution=2.0)
    assert df["sst_c"].between(12, 28).all(), f"SST out of range:\n{df['sst_c'].describe()}"


def test_ph_in_range(tmp_path):
    df = generate_env_grid(output_path=str(tmp_path / "env.csv"), resolution=2.0)
    assert df["ph"].between(7.95, 8.25).all(), f"pH out of range:\n{df['ph'].describe()}"


def test_salinity_in_range(tmp_path):
    df = generate_env_grid(output_path=str(tmp_path / "env.csv"), resolution=2.0)
    assert df["salinity_psu"].between(36.0, 39.0).all()


def test_depth_in_range(tmp_path):
    df = generate_env_grid(output_path=str(tmp_path / "env.csv"), resolution=2.0)
    assert df["mean_depth_m"].between(5, 200).all()


def test_reproducible_with_same_seed(tmp_path):
    df1 = generate_env_grid(output_path=str(tmp_path / "env1.csv"), resolution=2.0, seed=42)
    df2 = generate_env_grid(output_path=str(tmp_path / "env2.csv"), resolution=2.0, seed=42)
    pd.testing.assert_frame_equal(df1, df2)
