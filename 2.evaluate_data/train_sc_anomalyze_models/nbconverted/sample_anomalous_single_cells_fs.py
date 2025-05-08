#!/usr/bin/env python
# coding: utf-8

# # Sample data from each well
# Deterministically sample data from each plate dataset and get the intersection of all features not containing nans.

# ### Import Libraries

# In[ ]:


import json
import pathlib
import sys

import pandas as pd

sys.path.append(str(pathlib.Path.cwd().parent / "utils"))
from DeterministicSampling import DeterministicSampling


# ## Define paths

# ### Inputs

# In[1]:


# Plate morphology data
sc_data_path = pathlib.Path(sys.argv[1]).resolve(strict=True)
sc_data_dir_name = sc_data_path.parent.name
plate_path = pathlib.Path(sc_data_path).resolve(strict=True)
platedf = pd.read_parquet(plate_path)

sampled_plate_jump_path = pathlib.Path(sys.argv[2])

anomaly_data_path = pathlib.Path(sys.argv[3]) / sc_data_dir_name
anomaly_data_path.mkdir(parents=True, exist_ok=True)
feat_col_path = anomaly_data_path / "feature_columns.json"


# ### Outputs

# In[2]:


plate_data_path = sampled_plate_jump_path / f"{plate_path.parent.name}.parquet"


# ## Save feature columns that don't contain NaNs

# In[ ]:


feat_cols = []
non_na_cols = platedf.columns[platedf.notna().all()].tolist()

if feat_col_path.exists():
    with feat_col_path.open("r") as feat_col_obj:
        feat_cols = json.load(feat_col_obj)
        feat_cols = list(set(non_na_cols) & set(feat_cols))

else:
    feat_cols = non_na_cols

with feat_col_path.open("w") as feat_col_obj:
    json.dump(feat_cols, feat_col_obj)


# ## Sample single-cell data by Hash

# In[3]:


ds = DeterministicSampling(
    _platedf=platedf,
    # Number of samples per plate needed to train the JUMP isolation forests
    # See identify_anomalous_single_cells_fs.py for more details
    # Only 8_000 are needed, however each sampling will likely not be exactly 8_000 samples.
    # To ensure a sufficient sample size I increased the threshold.
    _samples_per_plate=8_100,
    _plate_column="Metadata_Plate",
    _well_column="Metadata_Well",
    _cell_id_columns=["Metadata_Site", "Metadata_ObjectNumber"],
)

sampled_platedf = ds.sample_plate_deterministically(_sample_strategy="well_sampling")


# ## Concatenate and Save Sampled Plate data

# In[4]:


if plate_data_path.exists():
    sampled_platedf = pd.concat(
        [sampled_platedf, pd.read_parquet(plate_data_path)], axis=0
    )

sampled_platedf.to_parquet(plate_data_path)

