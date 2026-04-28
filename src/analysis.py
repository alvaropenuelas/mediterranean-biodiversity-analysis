import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path

FIGURES_DIR = Path("outputs/figures")


def load_and_merge(
    obis_path="data/raw/obis_mediterranean.csv",
    env_path="data/raw/env_mediterranean.csv",
    processed_path="data/processed/merged_mediterranean.csv",
):
    obis = pd.read_csv(obis_path)
    env = pd.read_csv(env_path)

    res = 0.5
    obis = obis.dropna(subset=["decimalLongitude", "decimalLatitude", "species"])
    obis["cell_lat"] = (obis["decimalLatitude"] // res * res).round(1)
    obis["cell_lon"] = (obis["decimalLongitude"] // res * res).round(1)
    obis["cell_key"] = obis["cell_lat"].astype(str) + "_" + obis["cell_lon"].astype(str)

    richness = (
        obis.groupby("cell_key")["species"]
        .nunique()
        .reset_index()
        .rename(columns={"species": "species_richness"})
    )

    merged = richness.merge(env, on="cell_key", how="inner")

    Path(processed_path).parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(processed_path, index=False)
    print(f"Merged dataset: {len(merged)} grid cells with observations")
    return merged, obis


def plot_richness_map(merged):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(14, 7))
    sc = ax.scatter(
        merged["lon"], merged["lat"],
        c=merged["species_richness"],
        cmap="YlOrRd", s=50, alpha=0.85, edgecolors="none",
    )
    plt.colorbar(sc, ax=ax, label="Species Richness")
    ax.set_xlabel("Longitude (°)")
    ax.set_ylabel("Latitude (°)")
    ax.set_title("Mediterranean Species Richness — OBIS (2000–2024), 0.5° grid")
    ax.set_xlim(-7, 37)
    ax.set_ylim(29, 47)
    ax.grid(alpha=0.2)
    plt.tight_layout()
    path = FIGURES_DIR / "fig1_species_richness_map.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved → {path}")


def plot_correlation_matrix(merged):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    cols = ["species_richness", "sst_c", "ph", "salinity_psu", "mean_depth_m"]
    labels = ["Richness", "SST (°C)", "pH", "Salinity (PSU)", "Depth (m)"]
    corr = merged[cols].corr(method="spearman")
    corr.index = labels
    corr.columns = labels
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="coolwarm",
        center=0, vmin=-1, vmax=1, ax=ax,
        linewidths=0.5, square=True, annot_kws={"size": 11},
    )
    ax.set_title("Spearman Correlation — Mediterranean Environmental Variables vs. Species Richness")
    plt.tight_layout()
    path = FIGURES_DIR / "fig2_correlation_matrix.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved → {path}")


def plot_sst_vs_richness(merged):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    x = merged["sst_c"]
    y = merged["species_richness"]
    slope, intercept, r, p, _ = stats.linregress(x, y)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(x, y, alpha=0.45, color="steelblue", edgecolors="none", s=30)
    x_line = np.linspace(x.min(), x.max(), 100)
    ax.plot(
        x_line, slope * x_line + intercept,
        color="crimson", linewidth=2,
        label=f"Linear fit   R² = {r**2:.3f},  p = {p:.4f}",
    )
    ax.set_xlabel("Sea Surface Temperature (°C)")
    ax.set_ylabel("Species Richness")
    ax.set_title("SST vs. Species Richness — Mediterranean (OBIS occurrences + synthetic env)")
    ax.legend()
    ax.grid(alpha=0.2)
    plt.tight_layout()
    path = FIGURES_DIR / "fig3_sst_vs_richness.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved → {path}")


def plot_temporal_trend(obis):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    if "year" not in obis.columns or obis["year"].isna().all():
        print("No year data in OBIS records — skipping temporal trend")
        return
    yearly = obis.dropna(subset=["year"]).copy()
    yearly["year"] = yearly["year"].astype(int)
    yearly = yearly[yearly["year"].between(2000, 2024)]
    trend = (
        yearly.groupby("year")["species"]
        .nunique()
        .reset_index()
        .rename(columns={"species": "unique_species"})
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(trend["year"], trend["unique_species"], marker="o", color="teal", linewidth=2)
    ax.fill_between(trend["year"], trend["unique_species"], alpha=0.15, color="teal")
    ax.set_xlabel("Year")
    ax.set_ylabel("Unique Species Observed")
    ax.set_title(
        "Temporal Trend in Mediterranean Species Observations (OBIS, 2000–2024)\n"
        "Note: reflects sampling effort — not necessarily true biodiversity change"
    )
    years = trend["year"].tolist()
    ax.set_xticks(years[::2])
    ax.tick_params(axis="x", rotation=45)
    ax.grid(alpha=0.2)
    plt.tight_layout()
    path = FIGURES_DIR / "fig4_temporal_trend.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved → {path}")
