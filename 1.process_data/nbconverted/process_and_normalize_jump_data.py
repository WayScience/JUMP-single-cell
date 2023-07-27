#!/usr/bin/env python
# coding: utf-8

# # Preprocess using pyctyominer and merge broad samples

# ## Imports

# In[ ]:


import time
from pathlib import Path
import numpy as np
import pandas as pd
from pycytominer import normalize
from pycytominer.cyto_utils.cells import SingleCells


# ## Find the root of the git directory
# This allows file paths to be referenced in a system agnostic way

# In[ ]:


# Get the current working directory
cwd = Path.cwd()

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


# ## Define Paths

# In[ ]:


# Input paths
big_drive_path = f"{root_dir}/big_drive"
sqlite_data_path = f"{big_drive_path}/data"
ref_path = f"{root_dir}/1.process_data/reference_plate_data"
barcode_platemap = f"{ref_path}/barcode_platemap.csv"

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

# ## Define functions

# In[ ]:


# Add the 'Metadata' prefix to column names
def add_metadata_prefix_to_column_names(df):
    """
    Parameters
    ----------
    df: pandas Dataframe

    Returns
    -------
    df: pandas Dataframe
        A dataframe with the column names prefixed with the string 'Metadata'
    """

    df.rename(columns=lambda x: f"Metadata_{x}", inplace=True)
    return df

# Fill in broad_sample "DMSO" for NaN and prefix the column names
def fill_dmso(df):
    """
    Parameters
    ----------
    df: pandas Dataframe
        A dataframe of the platemap data and a corresponding 'broad_sample' column

    Returns
    -------
    df: pandas Dataframe
    A dataframe with without empty broad_samples and renamed columns
    """

    df["broad_sample"] = df["broad_sample"].fillna("DMSO")
    df = add_metadata_prefix_to_column_names(df)
    return df


# ## Map reference data

# In[ ]:


# Merge on the broad_sample column
merge_col = "Metadata_broad_sample"

compdf = pd.read_csv(f"{ref_path}/JUMP-Target-1_compound_metadata_targets.tsv", sep="\t")

# Set empty broad samples to DMSO if the pert iname is DMSO for the compounds dataframe
compdf.loc[compdf["pert_iname"] == "DMSO", "broad_sample"] = "DMSO"

# Map platemap names found in the barcode file to metadata dataframes
barcode_map = {"JUMP-Target-1_orf_platemap": pd.read_csv(f"{ref_path}/JUMP-Target-1_orf_metadata.tsv", sep="\t"),
               "JUMP-Target-1_crispr_platemap": pd.read_csv(f"{ref_path}/JUMP-Target-1_crispr_metadata.tsv", sep="\t"),
                "JUMP-Target-1_compound_platemap": compdf}

# Map platemap names found in the barcode file to platemap dataframes
platemeta2df = {platemap_name: pd.read_csv(f"{ref_path}/{platemap_name}.txt", sep="\t") for platemap_name, _ in barcode_map.items()}

# Map the wells corresponding to the empty broad samples in the plate metadata files
platemeta2cols = {name: df.loc[df["broad_sample"].isnull()]["well_position"].tolist() for name, df in platemeta2df.items() if name != "JUMP-Target-1_compound_platemap"}


# ## Rename columns and fill control values

# In[ ]:


# Rename colunns in plate metadata
barcode_map = {df_name: add_metadata_prefix_to_column_names(df) for df_name, df in barcode_map.items()}

# Fill the broad_sample missing values with DMSO for the plate metadata
platemeta2df = {df_name: fill_dmso(df) for df_name, df in platemeta2df.items()}


# ## Merge and Normalize plate data

# In[1]:


# Record the start time
start_time = time.time()

# Iterate through each plate in the barcode dataframe
for idx, row in barcode_df.iterrows():

    # Get the plate name
    plate_name = row["Assay_Plate_Barcode"]

    # Get the platemap name
    plate_map = row["Plate_Map_Name"]

    # Get the plate metadata dataframe from the platemap name
    broad_mapdf = barcode_map[plate_map]

    # Final path of each cell count output file
    output_cell_count_file = f"{output_cell_count_path}/{plate_name}_cellcount.tsv"

    # Path of each normalized out single cell dataset
    output_file = f"{normalized_path}/{plate_name}_normalized_sc.parquet"

    # Path of the original sqlite file
    sqlite_file = f"sqlite:///{sqlite_data_path}/{plate_name}.sqlite"

    # Create dataframe from plate metadata
    platemeta_df = platemeta2df[plate_map]

    # Get the single cell data
    sc = SingleCells(sql_file=sqlite_file, default_datatype_float=np.float32)

    # Output the cell count data
    cell_count_df = sc.count_cells()
    cell_count_df.to_csv(output_cell_count_file, sep="\t", index=False)

    # Merge single cells
    sc_df = sc.merge_single_cells(platemap=platemeta_df)

    # Merge the dataframes based on the broad_sample column
    sc_df = pd.merge(sc_df, broad_mapdf, how="left", on=merge_col)

    # We only change the columns if the plate does not contain empty wells
    if plate_map != "JUMP-Target-1_compound_platemap":
        sc_df.loc[sc_df["Metadata_Well"].isin(platemeta2cols[plate_map]), broad_mapdf.columns] = "no_treatment"

    # Normalize the data
    normalize(
        profiles=sc_df,
        features="infer",
        image_features=False,
        meta_features="infer",
        samples="Metadata_control_type == 'negcon'",
        method="standardize",
        output_file=output_file,
        output_type="parquet",
    )

# Record the end time
end_time = time.time()


# ## Specify the time taken

# In[2]:


t_minutes = (end_time - start_time) // 60
t_hours = t_minutes / 60
print(f"Total time taken = {t_minutes} minutes")
print(f"Total time taken = {t_hours} hours")

