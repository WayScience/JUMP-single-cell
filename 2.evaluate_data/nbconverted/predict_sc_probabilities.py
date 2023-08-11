#!/usr/bin/env python
# coding: utf-8

# # Predict Single Cell Probabilities
# In this part of the analysis, the single cell probabilities are predicted and stored in a parquet file.
# The index of this file is used to reference the single cell index in the corresponding parquet files, where the "Metadata_plate" column refers to the plate name corresponding to the reference file.

# ### Import Libraries

# In[1]:


import gzip
import io
import pathlib

import pandas as pd
import requests
from joblib import load


# ## Find the path of the git directory

# In[2]:


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

# In[3]:


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
    content = response.content
    file_object = io.BytesIO(content)

    if ".csv" in url:
        file_object = gzip.GzipFile(fileobj=file_object)
        obj = pd.read_csv(file_object)

    elif ".joblib" in url:
        obj = load(file_object)

    return obj


# In[4]:


# The paths of the models
model_paths = ["https://github.com/WayScience/phenotypic_profiling_model/raw/main/2.train_model/models/multi_class_models/final__CP.joblib", "https://github.com/WayScience/phenotypic_profiling_model/raw/main/2.train_model/models/multi_class_models/shuffled_baseline__CP.joblib"]

# The path of the data used for the data used for inferencing in the phenotypic_profiling_model repo
data_path = "https://github.com/WayScience/phenotypic_profiling_model/raw/main/0.download_data/data/labeled_data.csv.gz"

# Path to the drive
drive_path = f"{root_dir}/big_drive"

# The predicted probabilities of the models on each cell from each plate
output_proba_path = f"{drive_path}/probability_sc_data"

# The path of the normalized sc data
norm_data_path = pathlib.Path(f"{drive_path}/normalized_sc_data")

# The path of the model's predicted probabilities
pathlib.Path(f"{output_proba_path}").mkdir(parents=True, exist_ok=True)


# ## Load the data

# In[5]:


# Store the models as a dictionary
models = {model_path.split("/")[-1].split("__")[0]: load_joblib_from_url(model_path) for model_path in model_paths}

# Original dataset used to select features for models
data = load_joblib_from_url(data_path)

# Data columns from original dataset
all_cols = data.columns


# ## Inference

# In[6]:


# Extract CP features from all columns depending on desired dataset
feature_cols = [col for col in all_cols if "CP__" in col]
feature_cols = [string.replace("CP_", "Nuclei") if "CP" in string else string for string in feature_cols]
feature_cols = pd.Index(feature_cols)
model_preds = []
cell_count = 0

# Iterate through the normalized plate paths
for plate in norm_data_path.iterdir():

    # Load the dataframe for the plate
    df = pd.read_parquet(plate)

    # Retrieve the name of the parquet file
    parquet_name = plate.name.split('_')[0]

    # Find columns that were in the original dataset used for inferencing, but not in the new dataset
    new_df_cols = feature_cols.difference(df.columns).tolist()

    # Set the columns found above to all zero values
    df[new_df_cols] = 0

    # Get the wells of the plate
    well = df["Metadata_Well"]

    # Get the plate of the dataframe
    plate_name = df["Metadata_Plate"].iloc[0]

    # Order the column based on order of columns used to train model
    df = df[feature_cols]

    # Convert dataframe to matrix
    df_mat = df.values

    # Calculate the number of cells
    cell_count += df_mat.shape[0]

    # Create predictions for each model
    for model_type, model in models.items():

        # Find the probabilities
        preds = model.predict_proba(df_mat)

        # Store the predictions using the models classes
        predsdf = pd.DataFrame(preds, columns=model.classes_)

        # Store the type of model
        predsdf["Metadata_model_type"] = model_type

        # Store the well data
        predsdf["Metadata_Well"] = well

        # Store the plate data
        predsdf["Metadata_plate"] = plate_name

        # Store the prediction dataframes
        model_preds.append(predsdf)

# Concatenate the model predictions
model_preds = pd.concat(model_preds)

# Save predictions
model_preds.to_parquet(f"{output_proba_path}/model_probabilities.parquet", index=True)

print(f"The total cell count is {cell_count}")

