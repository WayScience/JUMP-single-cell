#!/usr/bin/env python
# coding: utf-8

# # Feature select and subset the features using the features used for the model of all JUMP plates 

# ## Import libraries

# In[1]:


import pyarrow.parquet as pq
import pandas as pd

import random
import pathlib

from pycytominer import feature_select


# ## Set paths and variables

# In[2]:


# path to normalized data
norm_dir = pathlib.Path(
    "../../../Way Science Lab Dropbox/JUMP Processed Data/normalized_sc_plate_data"
)

# path to saving the concat file
save_dir = pathlib.Path("./data")
save_dir.mkdir(parents=True, exist_ok=True)

# path to save normalized concat file
concat_save_path = pathlib.Path(f"{save_dir}/concat_norm_data_subset.parquet")

# URL path to Mitocheck labeled data
mitocheck_labeled_data_url = "https://github.com/WayScience/phenotypic_profiling_model/raw/main/0.download_data/data/labeled_data__ic.csv.gz"

# set feature selection operations (added get na columns due to issue when trying to create UMAP)
feature_select_ops = [
    "variance_threshold",
    "correlation_threshold",
    "blocklist",
    "drop_na_columns",
]

# set save path for feature selected concat file
fs_save_path = pathlib.Path(f"{save_dir}/concat_fs_norm_data_subset.parquet")

# path to save filtered subset data with Mitocheck features
filter_save_path = pathlib.Path(f"{save_dir}/concat_mitocheck_data_subset.parquet")

print("There are this many plates in this dataset:", len(list(norm_dir.glob("*"))))


# ## Concat a subset of all plates together into a dataframe and save the parquet file

# In[3]:


# Check to make sure the concatenated file doesn't already exist
if not concat_save_path.exists():
    # Create an empty DataFrame to store the concatenated data
    concatenated_df = pd.DataFrame()
    
    # Iterate through each Parquet file in the directory
    for file_path in norm_dir.glob("*.parquet"):
        print("Sampling from plate:", file_path.stem.split("_")[0])
        # Open the Parquet file
        parquet_file = pq.ParquetFile(file_path)

        # Get the number of rows in the file
        num_rows = parquet_file.num_row_groups

        # Randomly select a row group from the file
        random_row_group = random.randint(0, num_rows - 1)

        # Read the selected row group with the specified number of rows
        df = parquet_file.read_row_group(random_row_group, columns=parquet_file.schema.names, use_threads=True).to_pandas()

        # Randomly sample rows from the selected row group
        sampled_rows = df.sample(n=1000, random_state=0)

        print(f"Sampled data frame has this many rows: {sampled_rows.shape[0]}")

        # Concatenate the sampled rows to the concatenated_data DataFrame
        concatenated_df = pd.concat([concatenated_df, sampled_rows], ignore_index=True)

        print(f"Concat data frame now has {concatenated_df.shape[0]} rows")

    # Save the concatenated DataFrame as a Parquet file
    concatenated_df.to_parquet(concat_save_path, index=False)
    
else:
    # read in the parquet file to use
    concatenated_df = pd.read_parquet(concat_save_path)
    print("Concatenated file already exists and has been loaded in!")


# ## Check to see what the concat file looks like and if it looks correct

# In[4]:


print(concatenated_df.shape)
concatenated_df.head(2)


# # Perform feature selection on concat data and check output

# In[5]:


# Check to make sure the concatenated file doesn't already exist
if not fs_save_path.exists():
    # perform feature selection on concat normalized data
    feature_select(
        concatenated_df,
        operation=feature_select_ops,
        output_file=fs_save_path,
        output_type="parquet"
    )
    
# load back in fs data to see if it worked
fs_df = pd.read_parquet(fs_save_path)

print(fs_df.shape)
fs_df.head(2)


# ## Use Mitocheck labelled dataset to filter the subset of data to nuclei features

# In[6]:


# load in labelled data as Data Frame
label_df = pd.read_csv(mitocheck_labeled_data_url, compression='gzip')

# Extract metadata columns from concat df
metadata_cols = [col for col in concatenated_df.columns if col.startswith("Metadata")]

# Extract CellProfiler nuclei features from Mitocheck data
feature_cols = [col for col in label_df.columns if "CP__" in col]
feature_cols = [string.replace("CP_", "Nuclei") if "CP" in string else string for string in feature_cols]
feature_cols = pd.Index(feature_cols)

# Find columns that are in the Mitocheck data but not the JUMP data
diff_columns = feature_cols.difference(concatenated_df.columns).tolist()

# Remove features not seen in JUMP from Mitocheck feature list
feature_cols = [item for item in feature_cols if item not in diff_columns]

# Add metadata with nuclei features from Mitocheck
filtered_df = concatenated_df[metadata_cols + feature_cols]

# Save the concatenated DataFrame as a Parquet file
filtered_df.to_parquet(filter_save_path, index=False)

print(filtered_df.shape)
filtered_df.head(2)

