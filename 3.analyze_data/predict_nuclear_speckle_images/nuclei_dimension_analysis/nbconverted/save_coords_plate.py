#!/usr/bin/env python
# coding: utf-8

# # Compute Plate Crop Dimensions

# In[ ]:


import pathlib
import sys

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


# # Inputs

# In[ ]:


metadata_path = pathlib.Path(sys.argv[1])

# Did not remove nans from parquet files
# so downstream code can decide how to handle this data.
platedf = pd.read_parquet(metadata_path)


# # Outputs

# In[ ]:


crop_dimensions_data_path = root_dir / f"big_drive/nuclei_crop_dimensions_jump"

crop_dimensions_data_path.mkdir(parents=True, exist_ok=True)

plate_dimensions_data_path = (
    root_dir
    / crop_dimensions_data_path
    / f"{metadata_path.stem}_nuclei_crop_dimensions.parquet"
)


# ## Determine Important Columns
# Columns to save

# In[ ]:


meta_cols = list(platedf.columns[platedf.columns.str.contains("Metadata")])
bounding_box_coord_cols = [
    "Nuclei_AreaShape_BoundingBoxMaximum_X",
    "Nuclei_AreaShape_BoundingBoxMinimum_X",
    "Nuclei_AreaShape_BoundingBoxMaximum_Y",
    "Nuclei_AreaShape_BoundingBoxMinimum_Y",
]

platedf["Nuclei_AreaShape_BoundingBoxDelta_X"] = (
    platedf["Nuclei_AreaShape_BoundingBoxMaximum_X"]
    - platedf["Nuclei_AreaShape_BoundingBoxMinimum_X"]
)


platedf["Nuclei_AreaShape_BoundingBoxDelta_Y"] = (
    platedf["Nuclei_AreaShape_BoundingBoxMaximum_Y"]
    - platedf["Nuclei_AreaShape_BoundingBoxMinimum_Y"]
)


# ## Save Crop Dimensions

# In[ ]:


kept_cols = (
    [
        "Nuclei_AreaShape_BoundingBoxDelta_Y",
        "Nuclei_AreaShape_BoundingBoxDelta_X",
    ]
    + meta_cols
    + bounding_box_coord_cols
)

platedf[kept_cols].to_parquet(plate_dimensions_data_path)

