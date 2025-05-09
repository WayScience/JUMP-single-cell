#!/usr/bin/env python
# coding: utf-8

# # Identify Single Cell Anomalies
# Here we train Anomalyze models on different pre-computed datasets.

# ### Import Libraries

# In[ ]:


import json
import pathlib
import sys

import joblib
import pandas as pd
import pyarrow.parquet as pq
from sklearn.ensemble import IsolationForest


# ## Define paths

# ### Inputs

# In[1]:


plate_data_path = pathlib.Path(sys.argv[1])
plate_data_name = plate_data_path.name
sampled_plate_jump_data_path = sys.argv[2]

sampled_platedf = pd.read_parquet(
    f"{sampled_plate_jump_data_path}/{plate_data_name}.parquet"
)

feature_columns_path = (
    pathlib.Path(sys.argv[3]) / plate_data_name / "feature_columns.json"
).resolve(strict=True)

with feature_columns_path.open("r") as feat_cols_obj:
    feat_cols = json.load(feat_cols_obj)


# ### Outputs

# In[ ]:


isoforest_path = pathlib.Path(sys.argv[4])
isoforest_path.mkdir(parents=True, exist_ok=True)

isoforest_path = pathlib.Path(
    isoforest_path / f"{plate_data_name}_isolation_forest.joblib"
)


# ## Train Anomalyze Models

# In[ ]:


meta_cols = [col for col in sampled_platedf.columns if "Metadata" in col]
featdf = sampled_platedf[feat_cols]

# If 1_600 trees are trained with 256 samples per tree, then
# 1_600 * 256 gives approximately the expected number of samples per tree.
# For some of the plate data, this number of samples can barely fit in memory.
# We also want to maximize the number of trees to learn many patterns for identifying anomalies.
# 256 is empirically the largest number of samples per tree that allowed outliers to be isolated better.
isofor = IsolationForest(n_estimators=1_600, random_state=0, n_jobs=-1)
isofor.fit(featdf)

joblib.dump(isofor, isoforest_path)

