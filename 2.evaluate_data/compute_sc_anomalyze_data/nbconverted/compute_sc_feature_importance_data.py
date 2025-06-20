#!/usr/bin/env python
# coding: utf-8

# # Compute Sample Feature Importances
# This notebook computes feature importances by dataset, treatment type, and by anomaly score.

# In[ ]:


import pathlib
import sys
import time

sys.path.append(str((pathlib.Path.cwd().parent / "utils").resolve(strict=True)))
from collections import defaultdict

import joblib
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from isolation_forest_data_feature_importance import IsoforestFeatureImportance
from sklearn.ensemble import IsolationForest


# ## Find the root of the git repo on the host system

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


# # Inputs

# In[ ]:


# Replace with your root folder path
anomaly_datasets_path = root_dir / "big_drive/sc_anomaly_data"

anomalyze_models_path = root_dir / "big_drive/isolation_forest_models"

plate_mapping_path = root_dir / "reference_plate_data/experiment-metadata.tsv"

plate_mappingdf = pd.read_csv(plate_mapping_path, sep="\t")[
    ["Assay_Plate_Barcode", "Perturbation"]
]


# # Outputs

# In[ ]:


feature_importances_path = root_dir / "big_drive/sc_feature_importances"
feature_importances_path.mkdir(parents=True, exist_ok=True)


# # Sample and Compute Feature feature_importances
# Sample and then compute feature importances between the most anomalous and the least anomalous cells.

# In[ ]:


model_suffix_name = "_isolation_forest.joblib"
merge_cols = [
    "Metadata_Plate",
    "Metadata_Well",
    "Metadata_Site",
    "Metadata_ObjectNumber",
]

plate_mappingdf.rename(
    columns={
        "Assay_Plate_Barcode": "Metadata_Plate",
        "Perturbation": "Metadata_treatment_type",
    },
    inplace=True,
)

# Number of each type of sample per dataset, treatment type, and by anomaly score limit
num_control_samples = 500
num_anomalous_samples = 500

for anomaly_dataset in anomaly_datasets_path.iterdir():

    feature_importancesdf = []
    anomaly_model_name = anomaly_dataset.stem + model_suffix_name
    morphology_dataset = root_dir / f"big_drive/{anomaly_dataset.stem}"
    anomalyze_model = joblib.load(anomalyze_models_path / anomaly_model_name)
    anomalyze_model.n_jobs = -1

    anomaly_paths = list(anomaly_dataset.rglob("*.parquet"))

    anomdf = pd.concat(
        [pd.read_parquet(path) for path in anomaly_paths], ignore_index=True
    )

    anomdf = pd.merge(
        left=anomdf, right=plate_mappingdf, on="Metadata_Plate", how="inner"
    )

    for treatment_type_name, treatment_typedf in anomdf.groupby(
        "Metadata_treatment_type"
    ):
        treatment_typedf.columns.tolist()

        for control_type in ["negcon", "anomalous"]:

            # Negative controls shouldn't be anomalous and vice versa
            if control_type == "negcon":
                morphologydf = treatment_typedf.loc[
                    treatment_typedf["Metadata_control_type"] == "negcon"
                ].nlargest(num_control_samples, "Result_anomaly_score")

            else:
                morphologydf = treatment_typedf.loc[
                    treatment_typedf["Metadata_control_type"] != "negcon"
                ].nsmallest(num_anomalous_samples, "Result_anomaly_score")

            # Morphology parquet files are separated by plate in each dataset
            for plate in morphologydf["Metadata_Plate"].unique():

                platedf = pd.read_parquet(
                    list(morphology_dataset.rglob(f"*{plate}*.parquet"))[0]
                )

                platedf = platedf[
                    merge_cols + anomalyze_model.feature_names_in_.tolist()
                ]

                morphologydf = pd.merge(
                    left=platedf, right=morphologydf, on=merge_cols, how="inner"
                )

                morphologydf = morphologydf[anomalyze_model.feature_names_in_.tolist()]

                # Isolation forest reference:
                # https://ieeexplore.ieee.org/document/4781136
                feature_importancesdf.append(
                    IsoforestFeatureImportance(
                        _estimators=anomalyze_model.estimators_,
                        _morphology_data=morphologydf,
                        _num_train_samples_per_tree=anomalyze_model.max_samples_,
                    )()
                )

                feature_importancesdf[-1] = feature_importancesdf[-1].assign(
                    Metadata_control_type=control_type
                )

                feature_importancesdf[-1] = feature_importancesdf[-1].assign(
                    Metadata_treatment_type=treatment_type_name
                )

    pd.concat(feature_importancesdf, axis=0).to_parquet(
        feature_importances_path / anomaly_dataset.stem
    )

