#!/usr/bin/env python
# coding: utf-8

# # Identify single cell anomalies
# In this analysis we compute single-cell anomaly data with anomalyze

# In[ ]:


import pathlib
import sys

import joblib
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from sklearn.ensemble import IsolationForest


# ## Define inputs and outputs

# In[ ]:


sc_data_path = sys.argv[1].resolve(strict=True)
sc_data_dir_name = sc_data_path.parent.name
scdf = pd.read_parquet(sc_data_path)

iso_forest = joblib.load(pathlib.Path(sys.argv[2]).resolve(strict=True))

anomaly_data_path = pathlib.Path(sys.argv[3]) / sc_data_dir_name
anomaly_data_path.mkdir(parents=True, exist_ok=True)


# In[ ]:


feat_cols = iso_forest.feature_names_in_
meta_cols = [col for col in scdf.columns if "Metadata" in col]


# ## Compute Anomaly Data

# In[ ]:


# Isolation forest reference:
# https://ieeexplore.ieee.org/document/4781136
scdf = scdf.assign(Result_inlier=iso_forest.fit_predict(scdf[feat_cols]))
scdf = scdf[meta_cols].assign(
    Result_anomaly_score=iso_forest.decision_function(scdf[feat_cols])
)

scdf.sort_values(by="Result_anomaly_score", ascending=True, inplace=True)

pq.write_to_dataset(
    pa.Table.from_pandas(
        scdf[
            meta_cols
            + [
                "Result_inlier",
                "Result_anomaly_score",
            ]
        ]
    ),
    root_path=anomaly_data_path,
)

