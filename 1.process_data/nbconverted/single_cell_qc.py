#!/usr/bin/env python
# coding: utf-8

# ## Perform single-cell quality control to remove erroneous, technical outlier segmentations
#
# Using coSMicQC, we decided on three morphology features (related to shape and intensity) to maximize removal of poor quality nuclei segmentations that could impact downstream analysis.
#
# The original indices are saved as a CSV file to be used for filtering downstream.

# ## Set papermill parameters

# In[1]:


# Papermill notebook parameters
# (including notebook cell tag).
# We set a default here which may be overridden
# during Papermill execution.
# See here for more information:
# https://papermill.readthedocs.io/en/latest/usage-parameterize.html
plate_id = "BR00117010"


# In[2]:


# Parameters
plate_id = "BR00116999"


# ## Import libraries

# In[3]:


from pathlib import Path

import cosmicqc
import pandas as pd
from cytodataframe import CytoDataFrame
from pyarrow import parquet

# ## Load in the plate data to process with only relevant metadata columns

# In[4]:


# set path to save qc results
qc_results_dir = Path("./qc_results")
qc_results_dir.mkdir(parents=True, exist_ok=True)

# form a path to the parquet file with single-cell profiles
merged_single_cells = f"/media/jenna/8TB-C/work/JUMP-single-cell/0.download_data/data/plates/{plate_id}/{plate_id}.parquet"

# read only the metadata from parquet file
parquet.ParquetFile(merged_single_cells).metadata


# In[5]:


# set a list of metadata columns for use throughout
metadata_cols = [
    "Metadata_ImageNumber",
    "Image_Metadata_Site",
    "Metadata_ObjectNumber",
    "Metadata_Plate",
    "Metadata_Well",
    "Image_Metadata_Col",
    "Image_Metadata_Row",
    "Image_FileName_CellOutlines",
    "Image_FileName_NucleiOutlines",
    "Image_FileName_OrigDNA",
    "Image_FileName_OrigRNA",
    "Nuclei_AreaShape_BoundingBoxMaximum_X",
    "Nuclei_AreaShape_BoundingBoxMaximum_Y",
    "Nuclei_AreaShape_BoundingBoxMinimum_X",
    "Nuclei_AreaShape_BoundingBoxMinimum_Y",
]

# read only metadata columns with feature columns used for outlier detection
df_merged_single_cells = pd.read_parquet(
    path=merged_single_cells,
    columns=[
        *metadata_cols,
        "Nuclei_AreaShape_FormFactor",
        "Nuclei_Intensity_MassDisplacement_DNA",
        "Nuclei_AreaShape_Compactness",
    ],
)
print(df_merged_single_cells.shape)
df_merged_single_cells.head()


# ## Create mapping for the outlines to the images for CytoDataFrame

# In[6]:


# create an outline and orig mapping dictionary to map original images to outlines
# note: we turn off formatting here to avoid the key-value pairing definintion
# from being reformatted by black, which is normally preferred.
# fmt: off
outline_to_orig_mapping = {
    rf"{record['Metadata_Well']}_s{record['Image_Metadata_Site']}--nuclei_outlines\.png":
    rf"r{record['Image_Metadata_Row']:02d}c{record['Image_Metadata_Col']:02d}f{record['Image_Metadata_Site']:02d}p(\d{{2}})-.*\.tiff"
    for record in df_merged_single_cells[
        [
            "Metadata_Well",
            "Image_Metadata_Row",
            "Image_Metadata_Col",
            "Image_Metadata_Site",
        ]
    ].to_dict(orient="records")
}
# fmt: on

next(iter(outline_to_orig_mapping.items()))


# ## Detect technically mis-segmented nuclei
#
# We define technically mis-segmented nuclei as segmentations that include more than one nuclei, under or over-segmentation, or segmentation of background/smudging.
#
# We are using the measurements in two different conditions:
#

# 1. Irregular shaped nuclei where the intensity based center is much different than the shape's center
#
# This condition looks to detect any technical outliers with irregular shape and very high difference in centeroids, which can be detecting multiple different types of technical outliers.
#
# - `FormFactor`, which detects how irregular the shape is.
# - `MassDisplacement`, which detects how different the segmentation versus intensity based centeroids are (which can reflect multiple nuclei within one segmentation).
# We understand that interesting phenotypes will occur, so we are going to evaluate if this will identify the mis-segmentationsb

# ### Detect outliers and show single-cell image crops with CytoDataFrame (cdf)

# In[7]:


# find irregular shaped nuclei using thresholds that maximizes
# removing most technical outliers and minimizes good cells
feature_thresholds = {
    "Nuclei_AreaShape_FormFactor": -2.35,
    "Nuclei_Intensity_MassDisplacement_DNA": 1.5,
}

irregular_nuclei_outliers = cosmicqc.find_outliers(
    df=df_merged_single_cells,
    metadata_columns=metadata_cols,
    feature_thresholds=feature_thresholds,
)

irregular_nuclei_outliers_cdf = CytoDataFrame(
    data=pd.DataFrame(irregular_nuclei_outliers),
    data_context_dir=f"/media/jenna/8TB-C/work/JUMP-download-images/JUMP-single-cell/0.download_data/data/images/{plate_id}/orig",
    data_outline_context_dir=f"/media/jenna/8TB-C/work/JUMP-download-images/JUMP-single-cell/0.download_data/data/images/{plate_id}/outlines",
    segmentation_file_regex=outline_to_orig_mapping,
)[
    [
        "Nuclei_AreaShape_FormFactor",
        "Nuclei_Intensity_MassDisplacement_DNA",
        "Image_FileName_OrigDNA",
    ]
]


print(irregular_nuclei_outliers_cdf.shape)
irregular_nuclei_outliers_cdf.sort_values(
    by="Nuclei_AreaShape_FormFactor", ascending=False
).head(2)


# ### Randomly sample outlier rows to visually inspect if the threshold looks to be optimized

# In[8]:


irregular_nuclei_outliers_cdf.sample(n=5, random_state=0)


# ### Generate a new dataframe to save the original indices for filtering prior to further preprocessing

# In[9]:


# Create a new dataframe for failed QC indices
failed_qc_indices = irregular_nuclei_outliers[metadata_cols].copy()
failed_qc_indices["original_index"] = failed_qc_indices.index  # Store original index
failed_qc_indices = failed_qc_indices.reset_index(drop=True)  # Reset index
failed_qc_indices["cqc.formfactor_displacement_outlier"] = True

print(failed_qc_indices.shape)
failed_qc_indices.head()


# 2. Nuclei segmentations with holes and also irregular shaped
#
# We need to include this extra condition as it was discovered that there were more poorly segmented cells not caught, especially those over-segmented nuclei that contained holes, which is not common for a nuclei segmentation.
#
# - `Compactness`, which detects irregular nuclei and nuclei containing holes.

# ### Detect outliers and show single-cell image crops with CytoDataFrame (cdf)

# In[10]:


# find mis-segmented nuclei due using thresholds that maximizes
# removing most technical outliers and minimizes good cells
feature_thresholds = {
    "Nuclei_AreaShape_Compactness": 4.05,
}

poor_nuclei_outliers = cosmicqc.find_outliers(
    df=df_merged_single_cells,
    metadata_columns=metadata_cols,
    feature_thresholds=feature_thresholds,
)

poor_nuclei_outliers_cdf = CytoDataFrame(
    data=pd.DataFrame(poor_nuclei_outliers),
    data_context_dir=f"/media/jenna/8TB-C/work/JUMP-download-images/JUMP-single-cell/0.download_data/data/images/{plate_id}/orig",
    data_outline_context_dir=f"/media/jenna/8TB-C/work/JUMP-download-images/JUMP-single-cell/0.download_data/data/images/{plate_id}/outlines",
    segmentation_file_regex=outline_to_orig_mapping,
)[
    [
        "Nuclei_AreaShape_Compactness",
        "Image_FileName_OrigDNA",
    ]
]


print(poor_nuclei_outliers_cdf.shape)
poor_nuclei_outliers_cdf.sort_values(
    by="Nuclei_AreaShape_Compactness", ascending=True
).head(2)


# ### Randomly sample outlier rows to visually inspect if the threshold looks to be optimized

# In[11]:


poor_nuclei_outliers_cdf.sample(n=5, random_state=0)


# ### Save the original indices for failed single cells to compressed CSV files

# In[12]:


# Create a new dataframe for poor nuclei outliers
poor_qc_indices = poor_nuclei_outliers[metadata_cols].copy()
poor_qc_indices["original_index"] = poor_qc_indices.index  # Store original index
poor_qc_indices = poor_qc_indices.reset_index(drop=True)  # Reset index
poor_qc_indices["cqc.compactness_outlier"] = True

# Merge both outlier dataframes on metadata columns and original_index
failed_qc_indices = failed_qc_indices.merge(
    poor_qc_indices, on=[*metadata_cols, "original_index"], how="outer"
)

# Fill missing values with False (ensuring only detected outliers are True)
failed_qc_indices[
    ["cqc.formfactor_displacement_outlier", "cqc.compactness_outlier"]
] = failed_qc_indices[
    ["cqc.formfactor_displacement_outlier", "cqc.compactness_outlier"]
].fillna(
    False
)

# Calculate percentage removed
num_outliers = failed_qc_indices["original_index"].nunique()
total_cells = len(df_merged_single_cells)
percentage_removed = (num_outliers / total_cells) * 100

# Save the indices for failed single-cells as a compressed CSV file
failed_qc_indices.to_csv(
    Path(f"{qc_results_dir}/{plate_id}_failed_qc_indices.csv.gz"), compression="gzip"
)  # noqa: E501

print(f"Failed QC indices shape: {failed_qc_indices.shape}")
print(f"Percentage of single cells removed: {percentage_removed:.2f}%")
failed_qc_indices.head()
