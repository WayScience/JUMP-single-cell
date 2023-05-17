#!/usr/bin/env python
# coding: utf-8

# ## Convert SQLite files to parquet
# 
# 1. Load SQLite manifest
# 2. Use CytoTable to merge single cells and convert to parquet
# 3. Save converted files to disk

# In[1]:


import pathlib
import pandas as pd

import cytotable


# In[2]:


# Set constants
manifest_file = pathlib.Path("metadata", "jump_sqlite_aws_file_locations.tsv")


# In[3]:


manifest_df = pd.read_csv(manifest_file, sep="\t")

print(manifest_df.shape)
manifest_df.head()


# In[4]:


"/".join(manifest_df.sqlite_file[2].split("/")[0:-1])


# In[5]:


what = cytotable.convert(
    source_path="/".join(manifest_df.sqlite_file[2].split("/")[0:-1]),
    dest_path="test.parquet",
    dest_datatype="parquet"
)

