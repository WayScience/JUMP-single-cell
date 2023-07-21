#!/usr/bin/env python
# coding: utf-8

# # Download sqlite plate data from aws
# Note, this script was not rerun to display the outputs for the sake of time. To download the data, you must be signed into your aws account

# ## Imports

# In[ ]:


import subprocess
import pathlib.Path


# ## Find the root of the git directory
# This allows file paths to be referenced in a system agnostic way

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


# ## Download the plate sqlite data from AWS S3

# In[ ]:


# Specify the data path for downloading the data
download_map = "jump_dataset.csv"

# Specify the location to save the data
save_location = f"{root_dir}/big_drive"

# Download the data using a bash script
subprocess.run(["bash", "download_jump_data.sh", download_map, save_location])
