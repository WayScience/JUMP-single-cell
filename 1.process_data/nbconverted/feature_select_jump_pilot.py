#!/usr/bin/env python
# coding: utf-8

# # Feature Select normalized JUMP Pilot Data

# ## Imports

# In[ ]:


import sys
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


# ## Paths

# ### Inputs

# In[ ]:


big_drive_path = f"{root_dir}/big_drive"
ref_path = f"{root_dir}/reference_plate_data"

# Feature selected sc data
feature_selected_plate_path = sys.argv[1]
feature_selected_df = pd.read_parquet(feature_selected_plate_path)

# Name of the plate
plate_name = sys.argv[2]


# ### Outputs

# In[ ]:


# Output paths
feature_selected_path = Path(f"{big_drive_path}/feature_selected_sc_data")

feature_selected_path.mkdir(parents=True, exist_ok=True)


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


# Path of each feature selected output single cell dataset
feature_selected_output = f"{feature_selected_path}/{plate_name}_feature_selected_sc.parquet"

# Feature select normalized data
feature_select(
    feature_selected_df,
    operation=feature_select_ops,
    na_cutoff=0,
    output_file=feature_selected_output,
    output_type="parquet",
)

