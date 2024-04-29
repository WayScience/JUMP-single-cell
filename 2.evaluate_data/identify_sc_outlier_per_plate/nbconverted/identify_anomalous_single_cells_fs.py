#!/usr/bin/env python
# coding: utf-8

# # Identify Single Cell Anomalies
# In this part of the analysis, the single cell are computed using an isolation forest.
# The index of this file is used to reference the single cell index in the corresponding parquet files, where the "Metadata_plate" column refers to the plate name corresponding to the reference file.

# ### Import Libraries

# In[ ]:


import pathlib

import pandas as pd
import sys
from sklearn.ensemble import IsolationForest


# ## Find the path of the git directory

# In[ ]:


# Get the current working directory
cwd = pathlib.Path.cwd()

if (cwd / ".git").is_dir():
    root_dir = cwd

else:
    root_dir = None
    for parent in cwd.parents:
        if (parent / ".git").is_dir():
            root_dir = parent
            break

# Check if a Git root directory was found
if root_dir is None:
    raise FileNotFoundError("No Git root directory found.")


# ## Define paths

# ### Inputs

# In[ ]:


big_drive_path = f"{root_dir}/big_drive"

# Feature selected sc data
feature_selected_plate_path = sys.argv[1]
feature_selected_df = pd.read_parquet(feature_selected_plate_path)

# Name of the plate
plate_name = sys.argv[2]


# ### Outputs

# In[ ]:


outlier_path = pathlib.Path(f"{big_drive_path}/outlier_sc_fs_plate_data")
outlier_path.mkdir(parents=True, exist_ok=True)


# ## Identify Single Cell Outliers

# In[ ]:


# Metadata columns
meta_cols = [col for col in feature_selected_df.columns if "Metadata" in col]

# Cellprofiler feature data
featdf = feature_selected_df.drop(columns=meta_cols)

# Calculate anomalies
isofor = IsolationForest(n_estimators=1000, random_state=0, n_jobs=-1)

# Store anomaly data
pd.DataFrame(
    {
        "Result_inlier": isofor.fit_predict(featdf),
        "Result_anomaly_score": isofor.decision_function(featdf),
        "Metadata_Site": feature_selected_df["Metadata_Site"],
        "Metadata_Well": feature_selected_df["Metadata_Well"],
        "Metadata_Plate": feature_selected_df["Metadata_Plate"],
        "Metadata_ObjectNumber": feature_selected_df["Metadata_ObjectNumber"]
    }
).to_parquet(f"{outlier_path}/single_cell_fs_outlier_plate_{plate_name}.parquet", index=True)

