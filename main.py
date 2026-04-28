import matplotlib
matplotlib.use("Agg")

from src.obis_loader import fetch_mediterranean_species
from src.env_generator import generate_env_grid
from src.analysis import (
    load_and_merge,
    plot_richness_map,
    plot_correlation_matrix,
    plot_sst_vs_richness,
    plot_temporal_trend,
)

if __name__ == "__main__":
    print("Step 1/6: Fetching Mediterranean species from OBIS API...")
    fetch_mediterranean_species()

    print("\nStep 2/6: Generating environmental grid...")
    generate_env_grid()

    print("\nStep 3/6: Merging datasets...")
    merged, obis = load_and_merge()

    print("\nStep 4/6: Plotting species richness map...")
    plot_richness_map(merged)

    print("\nStep 5/6: Plotting correlation matrix and SST scatter...")
    plot_correlation_matrix(merged)
    plot_sst_vs_richness(merged)

    print("\nStep 6/6: Plotting temporal trend...")
    plot_temporal_trend(obis)

    print("\nDone. All figures saved to outputs/figures/")
