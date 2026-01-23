#!/usr/bin/env python
# coding: utf-8

# # Sample JUMP plate data to compute UMAP.
# This UMAP data was computed by sampling QC'd and feature-selected cellprofiler profiles.

# In[1]:


import pathlib
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import umap


# # Inputs

# In[2]:


root_path = pathlib.Path("../../")
big_drive_path = root_path / "big_drive"
feature_data_path = big_drive_path / "feature_selected_sc_qc_data"
anomaly_data_path = big_drive_path / "sc_anomaly_data/feature_selected_sc_qc_data"
plate_to_treat_typedf = pd.read_csv(
    (root_path / "reference_plate_data/barcode_platemap.csv").resolve(strict=True)
)
plate_to_treat_typedf = plate_to_treat_typedf.rename(
    columns={
        "Assay_Plate_Barcode": "Metadata_Plate",
        "Plate_Map_Name": "Metadata_Treatment_Type",
    }
)


# # Outputs

# In[3]:


umap_data_path = big_drive_path / "umap_data/feature_selected_sc_qc_data"
umap_data_path.mkdir(parents=True, exist_ok=True)


# ## Process Plate Mappings

# In[4]:


replacements = {
    "crispr": "crispr",
    "orf": "orf",
    "compound": "compound",
}

conditions = [
    plate_to_treat_typedf["Metadata_Treatment_Type"].str.contains(
        k, case=False, na=False
    )
    for k in replacements
]
choices = list(replacements.values())

plate_to_treat_typedf["Metadata_Treatment_Type"] = np.select(
    conditions, choices, default=plate_to_treat_typedf["Metadata_Treatment_Type"]
)


# # Sample Single Cells
# Sample cells from plate data.

# In[5]:


merge_cols = [
    "Metadata_Plate",
    "Metadata_Site",
    "Metadata_Well",
    "Metadata_ObjectNumber",
]

umapdf = []

for plate_path in feature_data_path.iterdir():
    plate_name = plate_path.stem.split("_")[0]

    print(f"Sampling Plate {plate_name}")
    anomaly_path = (
        big_drive_path
        / f"sc_anomaly_data/feature_selected_sc_qc_data/{plate_name}_feature_selected_sc_qc"
    )

    anomalydf = pd.concat(
        [pd.read_parquet(path) for path in anomaly_path.iterdir()], axis=0
    )

    featdf = pd.read_parquet(
        big_drive_path
        / f"feature_selected_sc_qc_data/{plate_name}_feature_selected_sc_qc.parquet"
    )

    result_cols = anomalydf.columns[anomalydf.columns.str.contains("Result")].tolist()

    # Include the anomaly data
    scdf = pd.merge(
        left=anomalydf[result_cols + merge_cols],
        right=featdf,
        how="inner",
        on=merge_cols,
    )

    # Include the treatment type
    scdf = pd.merge(
        left=scdf, right=plate_to_treat_typedf, how="inner", on="Metadata_Plate"
    )

    scdf.loc[
        ~scdf["Metadata_control_type"].isin(["negcon"]), "Metadata_control_type"
    ] = "other"

    scdf = scdf.groupby(["Metadata_control_type"], group_keys=False).sample(
        n=250, random_state=0
    )

    umapdf.append(scdf)

umapdf = pd.concat(umapdf, axis=0)
umapdf = umapdf.dropna(axis=1, how="any")

print("Shape of plate data after sampling:", umapdf.shape)
umapdf["Metadata_control_type"].unique()


# # Compute UMAP Components
# Drop all feature data not associated with UMAP, result, or metadata data.

# In[6]:


def compute_umap_components(umapdf: pd.DataFrame):
    umap_drop_cols = [
        col for col in umapdf.columns if "Metadata" in col or "Result" in col
    ]

    umapdf = umapdf.sample(frac=1, random_state=0)
    reducer = umap.UMAP(n_components=2, random_state=0)
    umap_data = reducer.fit_transform(umapdf.drop(columns=umap_drop_cols))
    umapdf["umap_0"], umapdf["umap_1"] = (
        umap_data[:, 0],
        umap_data[:, 1],
    )

    return umapdf[umap_drop_cols + ["umap_0", "umap_1"]]


umapdf = compute_umap_components(umapdf=umapdf)


# In[7]:


print("\nColumns of final umap:", umapdf.columns.tolist())
print(f"\nShape of final umap: {umapdf.shape}")
print(umapdf["Metadata_control_type"].value_counts())


# # Save UMAP Data

# In[8]:


umapdf.to_parquet(umap_data_path / "umap_feature_selected_sc_qc_data.parquet")

