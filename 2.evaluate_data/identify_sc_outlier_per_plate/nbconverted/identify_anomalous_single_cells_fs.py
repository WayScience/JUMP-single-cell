#!/usr/bin/env python
# coding: utf-8

# # Identify Single Cell Anomalies
# Here we train Anomalyze models on different pre-computed datasets.

# ### Import Libraries

# In[ ]:


import pathlib
import sys

import joblib
import pandas as pd
import pyarrow.parquet as pq
from sklearn.ensemble import IsolationForest


# ## Define paths

# ### Inputs

# In[1]:


plate_data_name = pathlib.Path(sys.argv[1]).name
is_sc = sys.argv[2].lower() == "true"
sampled_plate_jump_data_path = sys.argv[3]

sampled_platedf = pd.read_parquet(
    f"{sampled_plate_jump_data_path}/{plate_data_name}.parquet"
)


# ### Outputs

# In[ ]:


isoforest_path = pathlib.Path("isolation_forest_models")
isoforest_path.mkdir(parents=True, exist_ok=True)

isoforest_path = pathlib.Path(
    isoforest_path / f"{plate_data_name}_isolation_forest.joblib"
)


# ## Train Anomalyze Models

# In[ ]:


meta_cols = [col for col in sampled_platedf.columns if "Metadata" in col]
featdf = sampled_platedf.drop(columns=meta_cols).dropna(axis=1, how="any")

# 1 is used because aggregated data contains fewer samples
num_estimators = 1_600 if is_sc else 1

isofor = IsolationForest(n_estimators=num_estimators, random_state=0, n_jobs=-1)
isofor.fit(featdf)

joblib.dump(isofor, isoforest_path)

