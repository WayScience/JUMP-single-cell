#!/usr/bin/env python
# coding: utf-8

# # Anomaly score differences with aggregation order
# Uncover if the order of aggregation substantially influences the anomaly score
# The two operations are:
# - Aggregated Profile: Aggregated single-cell profiles to treatment level -> Trained with anomalyze to compute anomaly scores
# - Aggregated Anomaly Score: Trained with anomalyze to compute anomaly scores -> Aggregated single-cell anomaly scores to treatment level

# In[1]:


import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde


# ## Inputs

# In[2]:


root_dir = pathlib.Path("../../").resolve(strict=True)

agg_anomdf = pd.read_parquet(
    root_dir
    / "big_drive/aggregated_anomaly_data/aggregated_treatment_anomaly_data.parquet"
)

sc_anom_paths = (
    root_dir / "big_drive/sc_anomaly_data/feature_selected_sc_qc_data"
).resolve(strict=True)


# ## Outputs

# In[3]:


figures_path = pathlib.Path("figures")
figures_path.mkdir(parents=True, exist_ok=True)


# ## Aggregate Anomaly Scores to Treatment Level

# In[4]:


agg_platedf = []

for plate_path in sc_anom_paths.iterdir():

    treatment_col_name = "Metadata_pert_iname"
    platedf = pd.concat(
        [
            pd.read_parquet(data_path)
            for data_path in plate_path.rglob("*.parquet")
        ],
        axis=0,
    )

    result_cols = platedf.columns[platedf.columns.str.contains("Result")]

    agg_mapping = dict.fromkeys(result_cols, "mean")
    agg_mapping |= {"Metadata_Plate": "first"}

    # Distinguish between Compound data and (CRISPR and ORF data)
    if not np.any(platedf.columns.str.contains(treatment_col_name)):
        treatment_col_name = "Metadata_gene"

    agg_platedf.append(
        platedf.groupby(treatment_col_name).agg(agg_mapping).reset_index()
    )

agg_platedf = pd.concat(agg_platedf, axis=0)


# ## Merge Aggregated Anomaly Data

# In[5]:


all_anomdf = pd.merge(
    agg_platedf,
    agg_anomdf,
    how="inner",
    on=["Metadata_Plate", "Metadata_gene", "Metadata_pert_iname"],
    suffixes=("_aggregated_anomaly_score", "_aggregated_profile"),
)


# ## Plot Anomaly Scores according to Aggregation Order

# In[6]:


x_col = "Result_anomaly_score_aggregated_anomaly_score"
y_col = "Result_anomaly_score_aggregated_profile"

plot_df = all_anomdf[[x_col, y_col]].dropna()
x = plot_df[x_col].to_numpy()
y = plot_df[y_col].to_numpy()

# Reference line: y = x
y_identity = x

# R^2 vs identity
ss_res = np.sum((y - y_identity) ** 2)
ss_tot = np.sum((y - y.mean()) ** 2)
r2 = 1 - (ss_res / ss_tot)

# Error metrics vs identity
mse = np.mean((y - y_identity) ** 2)
mae = np.mean(np.abs(y - y_identity))

# Plot limits for identity line and for placing KDEs
line_min = min(x.min(), y.min())
line_max = max(x.max(), y.max())

plt.figure(figsize=(7, 6))

# Scatter
plt.scatter(x, y, s=20, alpha=0.6, edgecolor="none", label="Treatments")

# Identity line
plt.plot(
    [line_min, line_max],
    [line_min, line_max],
    color="crimson",
    linewidth=2,
    linestyle="--",
    label="Reference line (y = x)",
)

# ----------------------------
# Axis-attached 1D KDE overlays
# ----------------------------
# Grids
x_grid = np.linspace(x.min(), x.max(), 300)
y_grid = np.linspace(y.min(), y.max(), 300)

# KDEs
x_kde = gaussian_kde(x)
y_kde = gaussian_kde(y)

x_dens = x_kde(x_grid)
y_dens = y_kde(y_grid)

# Normalize to [0, 1] so we can scale into a small band on the axes
x_dens = x_dens / x_dens.max() if x_dens.max() > 0 else x_dens
y_dens = y_dens / y_dens.max() if y_dens.max() > 0 else y_dens

# Scale KDE size relative to the data ranges (tweak these)
x_range = line_max - line_min
y_range = line_max - line_min
kde_height = 0.08 * y_range  # vertical thickness of bottom KDE band
kde_width = 0.08 * x_range  # horizontal thickness of left KDE band

# Bottom KDE (distribution of x)
plt.fill_between(
    x_grid,
    line_min,
    line_min + x_dens * kde_height,
    color="gray",
    alpha=0.25,
    linewidth=0,
)

# Left KDE (distribution of y)
plt.fill_betweenx(
    y_grid,
    line_min,
    line_min + y_dens * kde_width,
    color="gray",
    alpha=0.25,
    linewidth=0,
)

# Keep the plot limits aligned with the identity line bounds
plt.xlim(line_min, line_max)
plt.ylim(line_min, line_max)

plt.xlabel("Aggregated Anomaly Scores")
plt.ylabel("Aggregated Profile Anomaly Scores")
plt.title("Aggregated Profile Anomaly Scores vs Aggregated Anomaly Scores")
plt.legend()
plt.tight_layout()

out_path = figures_path / "anomaly_comparisons.png"
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.show()

print(
    f"Reference line slope: 1.0, Intercept: 0.0, R^2 (vs y=x): {r2:.4f}, "
    f"MSE: {mse:.6f}, MAE: {mae:.6f}"
)

