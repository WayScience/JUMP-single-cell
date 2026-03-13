#!/usr/bin/env python
# coding: utf-8

# # Download and Save Image Metadata

# In[1]:


from pathlib import Path, PurePosixPath

import pandas as pd
import s3fs


# ## Paths and Names

# In[2]:


bucket = "cellpainting-gallery"
run_name = "2020_11_04_CPJUMP1"
prefix = f"cpg0000-jump-pilot/source_4/workspace/load_data_csv/{run_name}"

output_csv = Path(f"image_metadata/{run_name}_all_plates.csv")

s3_glob = f"{bucket}/{prefix}/*/load_data.csv"


# ## Download and Concatenate Metadata

# In[3]:


storage_options = {"anon": True}

fs = s3fs.S3FileSystem(anon=True)
csv_keys = sorted(fs.glob(s3_glob))

if not csv_keys:
    raise FileNotFoundError(f"No files found for pattern: s3://{s3_glob}")

print(f"Found {len(csv_keys)} plate CSV files under {run_name}")

dfs = []
for key in csv_keys:
    s3_url = f"s3://{key}"
    plate = PurePosixPath(key).parts[-2]

    print(f"Reading: {s3_url}")
    df = pd.read_csv(s3_url, storage_options=storage_options)
    df["source_plate"] = plate
    df["source_s3_path"] = s3_url
    dfs.append(df)

merged_df = pd.concat(dfs, axis=0, ignore_index=True)


# ## Save Metadata

# In[4]:


output_csv.parent.mkdir(parents=True, exist_ok=True)
merged_df.to_csv(output_csv, index=False)

print(f"Saved merged CSV to: {output_csv}")
print(f"Merged shape: {merged_df.shape}")

