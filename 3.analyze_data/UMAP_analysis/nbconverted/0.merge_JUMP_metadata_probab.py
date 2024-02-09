#!/usr/bin/env python
# coding: utf-8

# # Add necessary metadata to all features model probability file

# ## Import libraries

# In[1]:


import pathlib
import pandas as pd


# ## Load in data frames

# In[2]:


prob_dir = pathlib.Path("../../../Way Science Lab Dropbox/JUMP Processed Data/sc_predicted_probabilities")

prob_df = pd.read_parquet(pathlib.Path(f"{prob_dir}/model_probabilities.parquet"))
metadata_df = pd.read_parquet(pathlib.Path(f"{prob_dir}/model_probabilities_meta_columns.parquet"))

print(metadata_df.shape)
metadata_df.head()


# ## Concat probability and necessary metadata

# In[3]:


concatenated_prob_df = pd.concat([prob_df, metadata_df[["Metadata_ObjectNumber_cytoplasm", "Metadata_Site"]]], axis=1)

concatenated_prob_df.rename(columns={"Metadata_plate": "Metadata_Plate"}, inplace=True)

concatenated_prob_df.to_parquet("./data/all_features_probabilities.parquet")

print(concatenated_prob_df.shape)
concatenated_prob_df.head()

