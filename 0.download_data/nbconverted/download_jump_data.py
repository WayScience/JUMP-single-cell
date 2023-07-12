#!/usr/bin/env python
# coding: utf-8

# # Download sqlite plate data from aws
# Must be signed into your aws account

# ## Imports

# In[ ]:


import subprocess
import os


# ## Download the plate sqlite data from AWS S3

# In[ ]:


# Get the home directory
home_directory = os.environ["HOME"]

# Specify the data path for downloading the data
download_map = "jump_dataset.csv"

# Specify the location to save the data
save_location = f"{home_directory}/projects/phenotypic_profiling_analysis/jump_test_dataset/big_drive/data2/"

# Download the data using a bash script
subprocess.run(["bash", "download_jump_data.sh", download_map, save_location])

