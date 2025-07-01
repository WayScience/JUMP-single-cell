#!/usr/bin/env python
# coding: utf-8

# # Compute Plate Feature Importances
# Created to prevent memory leakage while computing feature importances by calling this script from a bash script

# In[ ]:


import argparse
import pathlib
import sys

import joblib
import pandas as pd

sys.path.append(str((pathlib.Path.cwd().parent / "utils").resolve(strict=True)))
from isolation_forest_data_feature_importance import IsoforestFeatureImportance


# # Inputs and Outputs

# In[ ]:


parser = argparse.ArgumentParser()
parser.add_argument("--anomaly_dataset_path", type=str, required=True)
parser.add_argument("--plate", type=str, required=True)
parser.add_argument("--morphology_dataset_path", type=str, required=True)
parser.add_argument("--model_path", type=str, required=True)
parser.add_argument("--feature_importances_output_path", type=str, required=True)
parser.add_argument("--plate_mapping_path", type=str, required=True)

args = parser.parse_args()

anomaly_dataset = pathlib.Path(args.anomaly_dataset_path)
morphology_dataset = pathlib.Path(args.morphology_dataset_path)
model_path = pathlib.Path(args.model_path)
feature_importances_output_path = pathlib.Path(args.feature_importances_output_path)
plate_mapping_path = pathlib.Path(args.plate_mapping_path)
anomalyze_model = joblib.load(model_path)


# # Compute Feature Importances

# In[ ]:


# Number of samples to compute feature importances for in each category (anomalous or inlier)
num_control_samples = 10
num_anomalous_samples = 10

merge_cols = [
    "Metadata_Plate",
    "Metadata_Well",
    "Metadata_Site",
    "Metadata_ObjectNumber",
]

plate_mappingdf = pd.read_csv(plate_mapping_path, sep="\t")[
    ["Assay_Plate_Barcode", "Perturbation"]
].rename(
    columns={
        "Assay_Plate_Barcode": "Metadata_Plate",
        "Perturbation": "Metadata_treatment_type",
    }
)

anomdf = pd.concat(
    [pd.read_parquet(path) for path in anomaly_dataset.rglob("*.parquet")],
    ignore_index=True,
)

feature_importancesdf = []


anomdf = anomdf.loc[anomdf["Metadata_Plate"] == args.plate]

for control_type in ["negcon", "anomalous"]:

    # Negative controls shouldn't be anomalous and vice versa
    if control_type == "negcon":
        morphologydf = anomdf.loc[
            (anomdf["Metadata_control_type"] == "negcon")
            & (anomdf["Metadata_Plate"] == args.plate)
        ].nlargest(num_control_samples, "Result_anomaly_score")

    else:
        morphologydf = anomdf.loc[
            (anomdf["Metadata_control_type"] != "negcon")
            & (anomdf["Metadata_Plate"] == args.plate)
        ].nsmallest(num_anomalous_samples, "Result_anomaly_score")

    platedf = pd.read_parquet(
        list(morphology_dataset.rglob(f"*{args.plate}*.parquet"))[0]
    )

    platedf = platedf[merge_cols + anomalyze_model.feature_names_in_.tolist()]

    morphologyonlydf = pd.merge(platedf, morphologydf, on=merge_cols, how="inner")
    morphologyonlydf = morphologyonlydf[anomalyze_model.feature_names_in_.tolist()]

    result = IsoforestFeatureImportance(
        estimators=anomalyze_model.estimators_,
        morphology_data=morphologyonlydf,
        num_train_samples_per_tree=anomalyze_model.max_samples_,
    )()

    result = result.assign(
        Metadata_control_type=control_type,
        Metadata_treatment_type=feature_importances_output_path.stem,
        Metadata_Plate=args.plate,
    )

    feature_importancesdf.append(result)

if feature_importancesdf:
    pd.concat(feature_importancesdf, axis=0).to_parquet(
        feature_importances_output_path / f"{args.plate}.parquet"
    )

