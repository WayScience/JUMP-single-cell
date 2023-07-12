#!/usr/bin/env python
# coding: utf-8

# # Preprocess using pyctyominer and merge broad samples

# ## Imports

# In[ ]:


import numpy as np
import pandas as pd

import time
from pathlib import Path
from pycytominer.cyto_utils.cells import SingleCells
from pycytominer import normalize
import os


# ## Define Paths

# In[ ]:


# Get the home directory
home_directory = os.environ["HOME"]

# Input paths
barcode_platemap = "barcode_platemap.csv"
broad_map = "repurposing_info_external_moa_map_resolved.tsv"
big_drive_path = f"{home_directory}/projects/phenotypic_profiling_analysis/jump_test_dataset/big_drive"
sqlite_data_path = f"{big_drive_path}/data"

# Output paths
output_cell_count_path = Path(f"{big_drive_path}/sc_counts")
normalized_path = Path(f"{big_drive_path}/normalized_sc_data")


# ## Create directories if non-existent

# In[ ]:


output_cell_count_path.mkdir(parents=True, exist_ok=True)
normalized_path.mkdir(parents=True, exist_ok=True)


# In[ ]:


# Create dataframe from barcode platemap
barcode_df = pd.read_csv(barcode_platemap)


# # Process cell data

# ## Rename broad columns for mapping

# In[ ]:


# Merge on the broad_sample column
merge_col = "Metadata_broad_sample"

broad_mapdf = pd.read_csv(broad_map, sep="\t")
broad_mapdf = broad_mapdf.rename(columns={"broad_sample": merge_col})
broad_mapdf = broad_mapdf[[merge_col, "moa", "pert_iname"]]
broad_mapdf = broad_mapdf.rename(
    columns={"moa": "Metadata_moa", "pert_iname": "Metadata_pert_iname"}
)


# In[1]:


start_time = time.time()

for idx, row in barcode_df.iterrows():

    # Get the plate map name from the barcode
    # plate_map_name = barcode_df.loc[barcode_df['Assay_Plate_Barcode'] == row['plate']]['Plate_Map_Name']
    plate_name = row["Assay_Plate_Barcode"]
    plate_map = row["Plate_Map_Name"]

    # Get the plate name
    output_cell_count_file = f"{output_cell_count_path}/{plate_name}_cellcount.tsv"
    output_file = f"{normalized_path}/{plate_name}_normalized_sc.parquet"
    sqlite_file = f"sqlite:///{sqlite_data_path}/{plate_name}.sqlite"

    # Specify the platemap file
    platemap_df = pd.read_csv(f"{plate_map}.txt", sep="\t")

    # Fill in broad_sample "DMSO" for NaN
    platemap_df.broad_sample = platemap_df.broad_sample.fillna("DMSO")
    platemap_df.columns = [f"Metadata_{x}" for x in platemap_df.columns]

    # Get the single cell data
    sc = SingleCells(sql_file=sqlite_file, default_datatype_float=np.float32)

    # Output the single cell data
    cell_count_df = sc.count_cells()
    cell_count_df.to_csv(output_cell_count_file, sep="\t", index=False)

    # Merge single cells
    sc_df = sc.merge_single_cells(platemap=platemap_df)

    # Merge the dataframes based on the broad_sample column
    sc_df = pd.merge(sc_df, broad_mapdf, how="left", on=merge_col)

    # Normalize the data
    normalize(
        profiles=sc_df,
        features="infer",
        image_features=False,
        meta_features="infer",
        samples="Metadata_broad_sample == 'DMSO'",
        method="standardize",
        output_file=output_file,
        output_type="parquet",
    )

end_time = time.time()


# In[2]:


t_minutes = (end_time - start_time) // 60
t_hours = t_minutes / 60
print(f"Total time taken = {t_minutes} minutes")
print(f"Total time taken = {t_hours} hours")

