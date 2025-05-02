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


sc_data_path = pathlib.Path(sys.argv[1]).resolve(strict=True)
sc_data_dir_name = sc_data_path.parent.name
pq_file = pq.ParquetFile(sc_data_path)

iso_forest = joblib.load(pathlib.Path(sys.argv[2]).resolve(strict=True))
iso_forest.n_jobs = -1

anomaly_data_path = pathlib.Path(sys.argv[3]) / sc_data_dir_name / sc_data_path.stem
anomaly_data_path.mkdir(parents=True, exist_ok=True)


# In[ ]:


feat_cols = iso_forest.feature_names_in_


# ## Compute Anomaly Data

# In[ ]:


# Isolation forest reference:
# https://ieeexplore.ieee.org/document/4781136
for i, batch in enumerate(pq_file.iter_batches(batch_size=220_000)):
    pdf = batch.to_pandas()
    meta_cols = [col for col in pdf.columns if "Metadata" in col]
    pdf = pdf.assign(Result_inlier=iso_forest.predict(pdf[feat_cols]))
    pdf = pdf.assign(Result_anomaly_score=iso_forest.decision_function(pdf[feat_cols]))

    pdf.sort_values(by="Result_anomaly_score", ascending=True, inplace=True)

    output_path = anomaly_data_path / f"{sc_data_path.stem}_anomaly_batch_{i}.parquet"
    pdf.to_parquet(output_path)

