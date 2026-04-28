import numpy as np
import pandas as pd
from pathlib import Path


def generate_env_grid(output_path="data/raw/env_mediterranean.csv", resolution=0.5, seed=42):
    rng = np.random.default_rng(seed)

    lons = np.arange(-6, 36, resolution)
    lats = np.arange(30, 46, resolution)

    rows = []
    for lat in lats:
        for lon in lons:
            # SST: warmer south and east; Mediterranean ranges 12–28°C
            sst_base = 20 + (lat - 38) * -0.4 + (lon - 15) * 0.1
            sst = float(np.clip(sst_base + rng.normal(0, 1.5), 12, 28))

            # pH: lower near coasts (river input), higher open ocean; ranges 7.95–8.25
            coast_dist = min(abs(lon - (-6)), abs(lon - 36)) / 42.0
            ph = float(np.clip(8.25 - (1 - coast_dist) * 0.15 + rng.normal(0, 0.02), 7.95, 8.25))

            # Salinity: higher in eastern basin; ranges 36–39 PSU
            salinity = float(np.clip(37.0 + (lon - 15) * 0.05 + rng.normal(0, 0.3), 36.0, 39.0))

            # Depth: proxy from distance to boundary; ranges 5–200 m
            shelf = min(abs(lat - 30), abs(lat - 46), abs(lon - (-6)), abs(lon - 36))
            depth = float(np.clip(shelf * 25 + rng.uniform(5, 50), 5, 200))

            rows.append({
                "lon": round(float(lon), 2),
                "lat": round(float(lat), 2),
                "cell_key": f"{round(float(lat), 1)}_{round(float(lon), 1)}",
                "sst_c": round(sst, 2),
                "ph": round(ph, 3),
                "salinity_psu": round(salinity, 2),
                "mean_depth_m": round(depth, 1),
            })

    df = pd.DataFrame(rows)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} grid cells → {output_path}")
    return df
