#!/usr/bin/env python
# coding: utf-8

# # Creates and stores the aws s3 plate data paths

# ## Imports

# In[1]:


import pathlib

import pandas as pd
import requests


# ## Create the output path if it doesn't exist

# In[2]:


output_path = pathlib.Path("data")
output_path.mkdir(parents=True, exist_ok=True)


# ## Store the plate paths

# In[3]:


source = "source_4"
batch = "2020_11_04_CPJUMP1"
data_locations = f"s3://cellpainting-gallery/cpg0000-jump-pilot/{source}/workspace/backend/{batch}"

# Repository owner
repo_owner = "jump-cellpainting"

# Repository name
repo_name = "pilot-cpjump1-data"

# Path to directory in the repo
directory_path = f"profiles/{batch}"

response = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{directory_path}")
data = response.json()

# Use the directory names from the repo to specicy the plate names
object_names = [item['name'] for item in data if item['type'] == 'dir']

sqlite_file = [f"{data_locations}/{obj_name['name']}/{obj_name['name']}.sqlite" for obj_name in data if obj_name['type'] == 'dir']

manifest_df = pd.DataFrame(
        {"plate": object_names,
         "sqlite_file": sqlite_file,
         })


# ## Save the paths data

# In[4]:


manifest_df.to_csv(output_path / "jump_dataset_location_manifest.csv", index=False)

