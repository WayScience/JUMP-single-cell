#!/usr/bin/env python
# coding: utf-8

# # Creates and stores the aws s3 plate data paths

# ## Imports

# In[1]:


import pathlib

import pandas as pd


# ## Find the root of the git repo on the host system

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


# ## Load a dataframe of plate names from the reference data

# In[3]:


filename = "barcode_platemap.csv"
plate_name_path = f"{root_dir}/reference_plate_data/{filename}"
plate_namedf = pd.read_csv(plate_name_path)


# ## Create the output path if it doesn't exist

# In[4]:


output_path = pathlib.Path("data")
output_path.mkdir(parents=True, exist_ok=True)


# ## Store the plate paths

# In[5]:


source = "source_4"
batch = "2020_11_04_CPJUMP1"
data_locations = f"s3://cellpainting-gallery/cpg0000-jump-pilot/{source}/workspace/backend/{batch}"

# Use the directory names from the repo to specicy the plate names
object_names = [item['Assay_Plate_Barcode'] for _, item in plate_namedf.iterrows()]

sqlite_file = [f"{data_locations}/{obj_name}/{obj_name}.sqlite" for obj_name in object_names]

manifest_df = pd.DataFrame(
        {"plate": object_names,
         "sqlite_file": sqlite_file,
         })


# ## Save the paths data

# In[6]:


manifest_df.to_csv(output_path / "jump_dataset_location_manifest.csv", index=False)

