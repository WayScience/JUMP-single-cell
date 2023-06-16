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
from parsl.config import Config
from parsl.executors import HighThroughputExecutor


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


parsl_config = Config(
    executors=[
        HighThroughputExecutor()
    ]
)


# In[ ]:


get_ipython().run_cell_magic('time', '', 'what = cytotable.convert(\n    source_path="/".join(manifest_df.sqlite_file[2].split("/")[0:-1]),\n    dest_path="test2.parquet",\n    dest_datatype="parquet",\n    chunk_size=150000,\n    parsl_config=parsl_config,\n    preset="cellprofiler_sqlite_pycytominer"\n)\n')


# In[ ]:




