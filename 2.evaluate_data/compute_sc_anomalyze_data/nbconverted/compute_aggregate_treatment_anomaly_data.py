#!/usr/bin/env python
# coding: utf-8

# # Compute Aggregate Treatment Anomaly Data
# Anomalies data are computed by first
# aggregating cellprofiler data to the treatment level, and
# then computing anomaly scores and feature importances for later analysis.

# In[ ]:


import pathlib
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

script_dir = (
    pathlib.Path(__file__).resolve().parent
    if "__file__" in globals()
    else pathlib.Path.cwd()
)
utils_dir = (script_dir.parent / "utils").resolve(strict=True)
sys.path.append(str(utils_dir))
from isolation_forest_data_feature_importance import IsoforestFeatureImportance


# ## Inputs

# In[ ]:


root_dir = pathlib.Path("../../").resolve(strict=True)
big_drive_path = pathlib.Path("/mnt/big_drive").resolve(strict=True)

agg_anomaly_data_path = (big_drive_path / "feature_selected_sc_qc_data").resolve(
    strict=True
)

exp_meta = pd.read_csv(
    root_dir / "reference_plate_data/experiment-metadata.tsv", sep="\t"
)


# ## Outputs

# In[ ]:


agg_treatment_anomaly_data_path = big_drive_path / "aggregated_anomaly_data"
agg_treatment_anomaly_data_path.mkdir(parents=True, exist_ok=True)


# ## Aggregate Treatment Profiles per Plate
# Aggregate the treatment profiles per plate, while
# also taking the intersection of all cellprofiler features.

# In[ ]:


exp_meta = exp_meta[["Assay_Plate_Barcode", "Perturbation"]]
agg_platedf = []
feat_cols = set()

for sc_plate_path in agg_anomaly_data_path.rglob("*.parquet"):
    morph_platedf = pd.read_parquet(sc_plate_path)
    treatment_col_name = "Metadata_pert_iname"
    plate_feat_cols = set(
        morph_platedf.columns[~morph_platedf.columns.str.contains("Metadata")].tolist()
    )

    if not feat_cols:
        feat_cols = plate_feat_cols
    else:
        feat_cols &= plate_feat_cols

    agg_mapping = dict.fromkeys(feat_cols, "mean")
    morph_platedf = morph_platedf.assign(Metadata_group_size=1)
    agg_mapping |= {"Metadata_group_size": "size", "Metadata_Plate": "first"}

    # Distinguish between Compound data and (CRISPR and ORF data)
    if not np.any(morph_platedf.columns.str.contains(treatment_col_name)):
        treatment_col_name = "Metadata_gene"

    agg_platedf.append(
        morph_platedf.groupby(treatment_col_name).agg(agg_mapping).reset_index()
    )

feat_cols = sorted(feat_cols)
agg_platedf = pd.concat(agg_platedf, axis=0)


# ## Merging and Processing Aggregate Profiles

# In[ ]:


agg_platedf = pd.merge(
    exp_meta,
    agg_platedf,
    how="inner",
    left_on="Assay_Plate_Barcode",
    right_on="Metadata_Plate",
)

agg_platedf = agg_platedf.rename(columns={"Perturbation": "Metadata_Perturbation"})


# ## Compute Aggregate Feature Importances
# Isolation forest reference:
# https://ieeexplore.ieee.org/document/4781136

# In[ ]:


isofor = IsolationForest(n_estimators=1_000, random_state=0, n_jobs=-1)
agg_platedf = agg_platedf.assign(
    **{
        "Result_inlier": isofor.fit_predict(agg_platedf[feat_cols]),
        "Result_anomaly_score": isofor.decision_function(agg_platedf[feat_cols]),
    }
)


# ## Compute Feature Importances
# Computes sample feature importances using anomaly scores per sample.

# In[ ]:


metadf = agg_platedf.copy().filter(regex="Metadata|Result")

result = IsoforestFeatureImportance(
    estimators=isofor.estimators_,
    morphology_data=agg_platedf[list(isofor.feature_names_in_)],
)()


# ## Combine Anomaly Results and Metadata

# In[ ]:


meta_resultdf = metadf[metadf.columns.difference(result.columns)]
result = result.join(meta_resultdf, how="inner")


# ## Save Aggregate Anomaly Data

# In[ ]:


result.to_parquet(
    agg_treatment_anomaly_data_path / "aggregated_treatment_anomaly_data.parquet"
)

