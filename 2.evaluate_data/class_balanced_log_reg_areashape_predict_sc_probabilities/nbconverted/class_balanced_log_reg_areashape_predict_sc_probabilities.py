#!/usr/bin/env python
# coding: utf-8

# # Predict Single Cell Probabilities
# In this part of the analysis, the predicted single cell probabilities are stored in parquet files per plate.
# Predicted probabilities are generated from a weighted logistic regression trained on AreaShape features from the mitocheck morphology features.

# ### Import Libraries

# In[ ]:


import gzip
import io
import pathlib
import sys

import pandas as pd
import requests
from joblib import load


# ## Find the path of the git directory

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


# ## Load data code

# In[ ]:


def load_joblib_from_url(url):
    """
    Retirieve joblib or gzip csv file from url

    Parameters
    ----------
    url : url
        The raw url of the file

    Returns
    -------
    obj : any Python object
    """

    response = requests.get(url)
    file_object = io.BytesIO(response.content)

    if ".csv" in url:
        file_object = gzip.GzipFile(fileobj=file_object)
        obj = pd.read_csv(file_object)

    elif ".joblib" in url:
        obj = load(file_object)

    return obj


# In[ ]:


# The path of the models used in the phenotypic_profiling_model repo
model_path = "https://github.com/WayScience/phenotypic_profiling_model/raw/main/2.train_model/models/multi_class_models"

# The path of the data used for the data used for inferencing in the phenotypic_profiling_model repo
data_path = "https://github.com/WayScience/phenotypic_profiling_model/raw/main/0.download_data/data/labeled_data__ic.csv.gz"

# Path to the drive
drive_path = f"{root_dir}/big_drive"

# The predicted probabilities of the models on each cell from each plate
output_proba_path = f"{drive_path}/class_balanced_log_reg_probability_sc_data"

# The path of the normalized sc data
norm_plate_path = sys.argv[1]

# The path of the unnormalized sc data
unnorm_plate_path = sys.argv[2]

# Name of the plate
plate_name = sys.argv[3]

# The path of the model's predicted probabilities
pathlib.Path(f"{output_proba_path}").mkdir(parents=True, exist_ok=True)


# ## Load the data

# In[ ]:


# Store the models as a dictionary
models = {
    "final":
        load_joblib_from_url(f"{model_path}/final__CP_areashape_only__balanced__ic.joblib"),
    "shuffled":
        load_joblib_from_url(f"{model_path}/shuffled_baseline__CP_areashape_only__balanced__ic.joblib")
}


# ## Specify probability data

# In[ ]:


# Original dataset used to select features for models
data = load_joblib_from_url(data_path)

# Extract CP features from all columns depending on desired dataset
feature_cols = [col for col in data.columns if ("CP__" in col) and ("AreaShape" in col)]
feature_cols = [string.replace("CP_", "Nuclei") if "CP" in string else string for string in feature_cols]
idx_feature_cols = pd.Index(feature_cols)

# Metadata columns
meta_cols = ["Metadata_Well", "Metadata_Plate", "Metadata_ObjectNumber_cytoplasm", "Metadata_Site"]

# Location columns to keep in the final output
loc_cols = ["Nuclei_Location_Center_Y", "Nuclei_Location_Center_X"]

# Load the unnormalized plate data
df_unnorm = pd.read_parquet(unnorm_plate_path)

# Only retain metadata columns
df_unnorm = df_unnorm[meta_cols]


# ## Save plate predicted probabilities

# In[ ]:


# Load the dataframe for the plate
df = pd.read_parquet(norm_plate_path)

# Find columns that were in the original dataset used for inferencing, but not in the new dataset
new_df_cols = idx_feature_cols.difference(df.columns).tolist()

# Set the feature columns present in the new plate data to zero
df[new_df_cols] = 0

# Store the models
modeldfs = []

for model_type, model in models.items():
    # Output dataframe (to be stored as an intermediate parquet file)
    modeldf = pd.DataFrame(
        model.predict_proba(df[feature_cols].values),
        columns=model.classes_
    )

    # Store the type of model
    modeldf["Metadata_model_type"] = model_type

    # Store the cytoplasm object number
    modeldf["Metadata_ObjectNumber_cytoplasm"] = df["Metadata_ObjectNumber_cytoplasm"]

    # Store the name of the plate
    modeldf["Metadata_Plate"] = df["Metadata_Plate"]

    # Store the name of the well
    modeldf["Metadata_Well"] = df["Metadata_Well"]

    # Store the name of the site
    modeldf["Metadata_Site"] = df["Metadata_Site"]

    # Add the nuclei locations (x,y)
    modeldf = modeldf.merge(df_unnorm, how="inner", on=meta_cols)

    modeldfs.append(modeldf)


# ## Save model probabilities

# In[ ]:


modeldfs = pd.concat(modeldfs)

# Save predictions in temporary location to free memory
modeldfs.to_parquet(f"{output_proba_path}/{plate_name}_class_balanced_log_reg_areashape_model_probabilities.parquet", index=True)

