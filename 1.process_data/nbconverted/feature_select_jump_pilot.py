#!/usr/bin/env python
# coding: utf-8

# # Feature Select normalized JUMP Pilot Data

# ## Imports

# In[ ]:


import time
from pathlib import Path

import pandas as pd
from pycytominer import feature_select


# ## Find the root of the git directory
# This allows file paths to be referenced in a system agnostic way

# In[ ]:


# Get the current working directory
cwd = Path.cwd()

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


# ## Define Paths

# In[ ]:


# Input paths
big_drive_path = f"{root_dir}/big_drive"
sqlite_data_path = f"{big_drive_path}/sc_data"
ref_path = f"{root_dir}/reference_plate_data"
barcode_platemap = f"{ref_path}/barcode_platemap.csv"
normalized_path = Path(f"{big_drive_path}/normalized_sc_data")

# Output paths
feature_selected_path = Path(f"{big_drive_path}/feature_selected_sc_data")

feature_selected_path.mkdir(parents=True, exist_ok=True)


# In[ ]:


# Create dataframe from barcode platemap
barcode_df = pd.read_csv(barcode_platemap)


# ## Feature selection parameters

# In[ ]:


feature_select_ops = [
    "variance_threshold",
    "correlation_threshold",
    "blocklist",
    "drop_na_columns",
]


# ## Merge, Normalize, and Feature Select plate data

# In[ ]:


# Record the start time
start_time = time.time()

# Iterate through each plate in the barcode dataframe
for idx, row in barcode_df.iterrows():

    plate_name = row["Assay_Plate_Barcode"]

    # Track progress
    print(f"\nProcessing Plate {plate_name}")

    # Path of each normalized output single cell dataset
    normalized_output = f"{normalized_path}/{plate_name}_normalized_sc.parquet"

    # Path of each feature selected output single cell dataset
    feature_selected_output = f"{feature_selected_path}/{plate_name}_normalized_sc.parquet"

    # Feature select normalized data
    feature_select(
        normalized_output,
        operation=feature_select_ops,
        na_cutoff=0,
        output_file=feature_selected_output,
        output_type="parquet",
    )

# Record the end time
end_time = time.time()


# ## Specify the time taken

# In[ ]:


t_minutes = (end_time - start_time) // 60
t_hours = t_minutes / 60
print(f"Total time taken = {t_minutes} minutes")
print(f"Total time taken = {t_hours} hours")

