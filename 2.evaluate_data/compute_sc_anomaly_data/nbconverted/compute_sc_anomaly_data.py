#!/usr/bin/env python
# coding: utf-8

# # Identify single cell anomalies
# In this analysis we compute single-cell anomaly data with anomalyze

# In[ ]:


import pathlib
import sys

import dask.dataframe as dd
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest


# ## Identify Anomaly Data

# In[ ]:


def compute_sc_anomalies(
    _scdf: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute single-cell outlier data.

    Parameters
    ----------
    _scdf: Single cell profile data containing morphology features and metadata.
    """

    # Isolation forest reference:
    # https://ieeexplore.ieee.org/document/4781136
    isofor = IsolationForest(n_estimators=1_000, random_state=0, n_jobs=-1)
    _scdf = _scdf.assign(Result_inlier=isofor.fit_predict(_scdf[feat_cols]))
    _scdf = _scdf[meta_cols].assign(
        Result_anomaly_score=isofor.decision_function(_scdf[feat_cols])
    )

    _scdf.sort_values(by="Result_anomaly_score", ascending=True, inplace=True)

    return _scdf[
        meta_cols
        + [
            "Result_inlier",
            "Result_anomaly_score",
        ]
    ]


# ## Define inputs and outputs

# In[ ]:


sc_data_path = pathlib.Path(sys.argv[1].resolve(strict=True))
scddf = dd.read_parquet(sc_data_path / "*.parquet")

iso_forest = joblib.load(pathlib.Path(sys.argv[2]).resolve(strict=True))

anomaly_data_path = pathlib.Path("sc_anomaly_data")
anomaly_data_path.mkdir(parents=True, exist_ok=True)


# In[ ]:


feat_cols = iso_forest.feature_names_in_
meta_cols = [col for col in scddf.columns if "Metadata" in col]

meta_dict = {col: scddf[col].dtype for col in meta_cols}
meta_dict["Result_inlier"] = "i1"  # int8
meta_dict["Result_anomaly_score"] = "f8"  # float64

# The "meta" parameter expects a dictionary describing the output dataframe column types.
outlier_ddf = scddf.map_partitions(compute_sc_anomalies, meta=meta_dict)
outlier_ddf.to_parquet(
    anomaly_data_path / sc_data_path.name / "_anomaly_data.parquet", write_index=False
)

