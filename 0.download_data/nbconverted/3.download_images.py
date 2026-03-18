#!/usr/bin/env python
# coding: utf-8

# # Download Pilot Images from Filtered Metadata
# Download JUMP Pilot Images using the filtered manifest metadata.

# In[1]:


import runpy

import pandas as pd


# ## Inputs

# In[2]:


mod = runpy.run_path("utils/download_images_from_metadata.py")
download_images_with_metadata = mod["download_images_with_metadata"]
img_metadf = pd.read_parquet("data/2020_11_04_CPJUMP1_all_plates.parquet")


# ## Filter Images to Download
# Don't filter images if you want to download all JUMP pilot (cpg0000) images

# In[3]:


img_metadf = img_metadf.iloc[:10]


# In[4]:


summary = download_images_with_metadata(
    df=img_metadf,
    url_column="Metadata_FileUrl",
    parallel=True,
    workers=16,
)
print(summary)

