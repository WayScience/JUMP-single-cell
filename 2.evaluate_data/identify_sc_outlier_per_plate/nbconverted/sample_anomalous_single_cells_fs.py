#!/usr/bin/env python
# coding: utf-8

# # Sample data from each well
# Deterministically sample data from each plate dataset

# ### Import Libraries

# In[ ]:


import pathlib
import sys

import pandas as pd

sys.path.append(str(pathlib.Path.cwd().parent / "utils"))
from DeterministicSampling import DeterministicSampling


# ## Define paths

# ### Inputs

# In[1]:


# Plate morphology data
plate_path = pathlib.Path(sys.argv[1]).resolve(strict=True)
platedf = pd.read_parquet(plate_path)

# Boolean flag for if the data is single-cell
is_sc = sys.argv[2].lower() == "true"

sampled_plate_jump_path = pathlib.Path(sys.argv[3])


# ### Outputs

# In[2]:


plate_data_path = sampled_plate_jump_path / f"{plate_path.parent.name}.parquet"


# ## Sample single-cell data by Hash

# In[3]:


if is_sc:
    ds = DeterministicSampling(
        _platedf=platedf,
        _samples_per_plate=8_100,
        _plate_column="Metadata_Plate",
        _well_column="Metadata_Well",
        _cell_id_columns=["Metadata_Site", "Metadata_ObjectNumber"],
    )

    sampled_platedf = ds.sample_plate_deterministically(
        _sample_strategy="well_sampling"
    )

else:
    sampled_platedf = platedf


# ## Concatenate and Save Sampled Plate data

# In[4]:


if plate_data_path.exists():
    sampled_platedf = pd.concat(
        [sampled_platedf, pd.read_parquet(plate_data_path)], axis=0
    )

sampled_platedf.to_parquet(plate_data_path)

print(sampled_platedf.shape)

