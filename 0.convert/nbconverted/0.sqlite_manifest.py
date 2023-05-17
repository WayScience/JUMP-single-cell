#!/usr/bin/env python
# coding: utf-8

# ## Process JUMP SQLite files
# 
# 1. Load file paths from AWS
# 2. Append perturbation types from https://github.com/jump-cellpainting/datasets
# 3. Output file manifest

# In[1]:


import boto3
import pathlib
import cloudpathlib
import pandas as pd


# In[2]:


# Set constants
jump_id = "cpg0016-jump"
s3_bucket_name = "cellpainting-gallery"
backend_directory = "workspace/backend/"

jump_data_commit = "4b24577c2d3228d92177b807fa53fbbc623da1cb"
jump_github = "https://github.com/jump-cellpainting/datasets/"
perturbation_type_url = f"{jump_github}/raw/{jump_data_commit}/metadata/plate.csv.gz"

output_file = pathlib.Path("metadata", "jump_sqlite_aws_file_locations.tsv")


# In[3]:


# Connect to Cell Painting gallery S3 session
# Note: you must have already configured awscli with credentials
session = boto3.Session()
s3 = session.resource("s3")

cell_painting_gallery = s3.Bucket(s3_bucket_name)


# In[4]:


# Use client to list source directories
# Sources represent different sites from the JUMP consortium
client = boto3.client("s3")

top_level_jump_result = client.list_objects(
    Bucket=s3_bucket_name,
    Prefix=f"{jump_id}/",
    Delimiter="/"
)

data_collection_sources = []
for source_directory in top_level_jump_result.get("CommonPrefixes"):
    data_collection_sources.append(source_directory.get("Prefix").split("/")[1])
    
data_collection_sources


# In[5]:


# Obtain batch names for each source
source_batch_dictionary = {}
for source in data_collection_sources:
    prefix_string_per_source = f"{jump_id}/{source}/{backend_directory}"
    
    source_prefix_where_batches_exist_client = client.list_objects(
        Bucket=s3_bucket_name,
        Prefix=prefix_string_per_source,
        Delimiter="/"
    )
    source_batch_dictionary[source] = []
    for batch_directory in source_prefix_where_batches_exist_client.get("CommonPrefixes"):
        source_batch_dictionary[source].append(batch_directory["Prefix"].split("/")[-2])
        
source_batch_dictionary


# In[6]:


# Get plate ids
source_plate_dictionary = {}
source_plate_info = []
for source, source_batches in source_batch_dictionary.items():
    source_plate_dictionary[source] = {}
    for batch in source_batches:
        # Note backend_directory = "workspace/backend/"
        prefix_string_per_batch = f"{jump_id}/{source}/{backend_directory}{batch}/"

        source_prefix_where_plates_exist_client = client.list_objects(
            Bucket=s3_bucket_name,
            Prefix=prefix_string_per_batch,
            Delimiter="/"
        )
        source_plate_dictionary[source][batch] = []

        for plate_directory in source_prefix_where_plates_exist_client.get("CommonPrefixes"):
            plate = plate_directory["Prefix"].split("/")[-2]
            source_plate_dictionary[source][batch].append(plate)
            
            # Build SQLite file
            sqlite_file = f"s3://{s3_bucket_name}/{prefix_string_per_batch}{plate}/{plate}.sqlite"
            source_plate_info.append([source, batch, plate, sqlite_file])


# In[7]:


# Compile JUMP data manifest
jump_df = pd.DataFrame(source_plate_info, columns=["source", "batch", "plate", "sqlite_file"])

# Append perturbation type to this dataframe
# Load metadata from https://github.com/jump-cellpainting/datasets
perturbation_type_df = pd.read_csv(perturbation_type_url)
perturbation_cols = ["Metadata_Source", "Metadata_Batch", "Metadata_Plate"]

jump_df = (
    jump_df.merge(
        perturbation_type_df,
        left_on=["source", "batch", "plate"],
        right_on=perturbation_cols,
        how="outer"
    )
    .drop(perturbation_cols, axis="columns")
)

# Output file
jump_df.to_csv(output_file, sep="\t", index=False)

print(jump_df.shape)
jump_df.head()


# In[8]:


jump_df.Metadata_PlateType.value_counts()

