#!/usr/bin/env python
# coding: utf-8

# # Aggregate JUMP Pilot Data

# ## Imports

# In[ ]:


import sys
from pathlib import Path

import pandas as pd
from pycytominer import aggregate


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

single_cell_plate_path = sys.argv[1]
single_cell_df = pd.read_parquet(single_cell_plate_path)

plate_name = sys.argv[2]

aggregation_name = sys.argv[3]


# ### Outputs

# In[ ]:


aggregation_path = Path(f"{big_drive_path}/{aggregation_name}_aggregated_data")

aggregation_path.mkdir(parents=True, exist_ok=True)


# ## Aggregate

# In[ ]:


aggregated_output = (
    f"{aggregation_path}/{plate_name}_{aggregation_name}_aggregated.parquet"
)

aggregate(
    population_df=single_cell_df,
    strata=["Metadata_Plate", "Metadata_Well"],
    features="infer",
    operation="mean",
    output_file=aggregated_output,
    output_type="parquet",
)

