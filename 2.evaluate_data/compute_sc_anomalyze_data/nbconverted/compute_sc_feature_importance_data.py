#!/usr/bin/env python
# coding: utf-8

# # Compute Sample Feature Importances
# This notebook computes feature importances by dataset, treatment type, and by anomaly score.

# In[ ]:


import argparse
import pathlib
import subprocess
import sys

sys.path.append(str((pathlib.Path.cwd().parent / "utils").resolve(strict=True)))

import joblib
import pandas as pd


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

parser = argparse.ArgumentParser()
parser.add_argument(
    "--big_drive_path",
    type=pathlib.Path,
    default=pathlib.Path("/mnt/big_drive"),
)
args = parser.parse_args()


# # Inputs

# In[ ]:


# Replace with your data storage path here
big_drive_path = args.big_drive_path.resolve(strict=True)
anomaly_datasets_path = (big_drive_path / "sc_anomaly_data").resolve(strict=True)

anomalyze_models_path = (big_drive_path / "isolation_forest_models").resolve(
    strict=True
)

plate_mapping_path = (
    root_dir / "reference_plate_data/experiment-metadata.tsv"
).resolve(strict=True)

plate_mappingdf = pd.read_csv(plate_mapping_path, sep="\t")[
    ["Assay_Plate_Barcode", "Perturbation"]
]


# # Outputs

# In[ ]:


feature_importances_path = big_drive_path / "sc_anomaly_feature_importances"


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

for anomaly_dataset in anomaly_datasets_path.iterdir():
    if "normal" in anomaly_dataset.stem or "qc" not in anomaly_dataset.stem:
        continue

    anomaly_model_name = anomaly_dataset.stem + model_suffix_name
    morphology_dataset = big_drive_path / f"{anomaly_dataset.stem}"
    anomalyze_model = joblib.load(anomalyze_models_path / anomaly_model_name)

    anomaly_paths = list(anomaly_dataset.rglob("*.parquet"))

    anomdf = pd.concat(
        [pd.read_parquet(path) for path in anomaly_paths], ignore_index=True
    )

    anomdf = pd.merge(
        left=anomdf, right=plate_mappingdf, on="Metadata_Plate", how="inner"
    )

    dataset_feature_importances_path = feature_importances_path / anomaly_dataset.stem

    for treatment_type_name, treatment_typedf in anomdf.groupby(
        "Metadata_treatment_type"
    ):
        treatment_feature_importances_path = (
            dataset_feature_importances_path / treatment_type_name
        )
        treatment_feature_importances_path.mkdir(parents=True, exist_ok=True)

        # Morphology parquet files are separated by plate in each dataset
        for plate in treatment_typedf["Metadata_Plate"].unique():
            subprocess.run(
                [
                    "run_feature_importance.sh",
                    str(anomaly_dataset),
                    plate,
                    str(morphology_dataset),
                    str(anomalyze_models_path / anomaly_model_name),
                    str(treatment_feature_importances_path),
                    str(plate_mapping_path),
                    "nbconverted/compute_feature_importance_by_plate.py",
                ]
            )
