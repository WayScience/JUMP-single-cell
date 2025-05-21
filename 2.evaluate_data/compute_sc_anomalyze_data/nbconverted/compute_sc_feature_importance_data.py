#!/usr/bin/env python
# coding: utf-8

# # Identify single cell anomalies
# In this analysis we compute single-cell anomaly data with anomalyze

# In[ ]:


import pathlib
import sys

sys.path.append(str((pathlib.Path.cwd().parent / "utils").resolve(strict=True)))
import joblib
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from isolation_forest_data_feature_importance import IsoforestFeatureImportance
from sklearn.ensemble import IsolationForest


# ## Define inputs and outputs

# In[ ]:


sc_data_path = pathlib.Path(sys.argv[1]).resolve(strict=True)
sc_data_dir_name = sc_data_path.parent.name
pq_file = pq.ParquetFile(sc_data_path)

iso_forest = joblib.load(pathlib.Path(sys.argv[2]).resolve(strict=True))
iso_forest.n_jobs = -1

feature_importance_data_path = (
    pathlib.Path(sys.argv[3]) / sc_data_dir_name / sc_data_path.stem
)
feature_importance_data_path.mkdir(parents=True, exist_ok=True)


# ## Compute Anomaly Data

# In[ ]:


# Isolation forest reference:
# https://ieeexplore.ieee.org/document/4781136
# The data is batched here to reduce the memory burden
for i, batch in enumerate(pq_file.iter_batches(batch_size=220_000)):
    morphologydf = batch.to_pandas()[iso_forest.feature_names_in_]
    IsoforestFeatureImportance(
        _estimators=iso_forest.estimators_,
        _morphology_data=morphologydf,
        _num_train_samples_per_tree=iso_forest.max_samples_,
    )().to_parquet(
        feature_importance_data_path
        / f"{sc_data_path.stem}_feature_importance_{i}.parquet"
    )

