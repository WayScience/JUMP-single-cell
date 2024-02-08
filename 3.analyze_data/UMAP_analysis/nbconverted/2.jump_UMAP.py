#!/usr/bin/env python
# coding: utf-8

# # Set up UMAP coordinates

# ## Import libraries

# In[1]:


import pathlib
import pandas as pd
import umap


# ## Set paths and variables

# In[2]:


# Load in barcode_platemap to assign plates based on treatment type
barcode_platemap = pd.read_csv(
    pathlib.Path("../../reference_plate_data/barcode_platemap.csv")
)

# Create a dictionary mapping plate to treatment type
plate_map_dict = dict(
    zip(barcode_platemap["Assay_Plate_Barcode"], barcode_platemap["Plate_Map_Name"])
)

# load in feature selected data
fs_df = pd.read_parquet(pathlib.Path("./data/concat_fs_norm_data_subset.parquet"))

# load in mitocheck filtered data
filter_df = pd.read_parquet(pathlib.Path("./data/concat_mitocheck_data_subset.parquet"))

# load in predicted probabilites file
prob_path = pathlib.Path("./data/all_features_probabilities.parquet")
prob_df = pd.read_parquet(prob_path)

# Mitocheck labelled dataset to use to find nuclei features and concat
label_data_path = "https://github.com/WayScience/phenotypic_profiling_model/raw/main/0.download_data/data/labeled_data__ic.csv.gz"

# Model type that will be used for the add predicted probability column
model_type = "final"

# UMAP results output directory
UMAP_results_dir = pathlib.Path("./results")
UMAP_results_dir.mkdir(exist_ok=True)

# Dict for data frames to be used for UMAP embeddings
df_dict = {}

print("We are working with a total of", fs_df.shape[0], "single-cells")
print(
    "There are these many features that were selected as differential:", fs_df.shape[1]
)


# ## Add treatment type as a column
# 
# Note: This will be either compound, crispr, or orf.

# In[3]:


# Add the Metadata_treatment column to concatenated_df
filter_df["Metadata_treatment"] = filter_df["Metadata_Plate"].map(plate_map_dict)

# Split the values in the Metadata_treatment column by "_" and take the 1st index
filter_df["Metadata_treatment"] = filter_df["Metadata_treatment"].str.split("_").str[1]

# move relevant metadata to the front of the data frame (treatment will be first)
desired_columns = [
    "Metadata_treatment",
    "Metadata_Plate",
    "Metadata_Well",
    "Metadata_Site",
    "Metadata_ObjectNumber_cytoplasm",
]
filter_df = filter_df[
    desired_columns + [col for col in filter_df if col not in desired_columns]
]

# Check to make sure that this metadata has been added
print(filter_df.shape)
filter_df.head(2)


# In[4]:


# Loop through the columns and add "Metadata_" prefix to the nuclei center x,y columns
for column in prob_df.columns:
    if column.startswith("Nuclei"):
        prob_df.rename(columns={column: "Metadata_" + column}, inplace=True)

prob_df = prob_df.rename(columns={"Metadata_plate": "Metadata_Plate"})

print(prob_df.shape)
prob_df.head()


# In[5]:


# Only use final model
filtered_prob_df = prob_df[prob_df["Metadata_model_type"] == model_type]

# Add predicted class for each row to use for labelling
# set to -7 only for greg model, other models can be -5 if they do not include center x,y coords
filtered_prob_df["Metadata_Predicted_Class"] = filtered_prob_df.iloc[:, :-7].idxmax(
    axis=1
)

# Include a new column called Metadata_Phenotypic_Value as to be able to plot on UMAP
# Take the highest prob value and add as a value in the column to use for labelling
filtered_prob_df["Metadata_Phenotypic_Value"] = filtered_prob_df.iloc[:, :-7].max(
    axis=1
)

print(filtered_prob_df.shape)
filtered_prob_df.head()


# In[6]:


# Specify the columns you want to use for merging morphology and probabilities
merge_columns = [
    "Metadata_Plate",
    "Metadata_Well",
    "Metadata_Site",
    "Metadata_ObjectNumber_cytoplasm",
]

# Select only the columns in filtered_prob_df that start with "Metadata"
filtered_prob_df_subset = filtered_prob_df.filter(like="Metadata")

# Merge the data frames on the specified columns
merged_prob_df = filter_df.merge(filtered_prob_df_subset, on=merge_columns, how="inner")

# Remove rows with NaN in feature columns
merged_prob_df = merged_prob_df.dropna(
    subset=(col for col in merged_prob_df.columns if not col.startswith("Metadata"))
)

# reset index
merged_prob_df.reset_index(inplace=True, drop=True)

# Add data frame to dictionary
df_dict["Only_JUMP_all_features"] = merged_prob_df

print(merged_prob_df.shape)
merged_prob_df.head(2)


# ## Combine data frames

# ### Remove all metadata and only include a metadata for data type

# In[7]:


# Find all columns that start with Metadata
metadata_cols = [col for col in merged_prob_df.columns if col.startswith("Metadata")]

# Create a new DataFrame by selecting only "Metadata_Predicted_Class" and all other columns
jump_df = merged_prob_df[
    ["Metadata_Predicted_Class", "Metadata_Phenotypic_Value"]
    + [col for col in merged_prob_df.columns if col not in metadata_cols]
]

# Add a data name column to separate between datasets
jump_df.insert(0, "Metadata_data_name", "jump")

print(jump_df.shape)
jump_df.head(2)


# ### Load in Mitocheck labeled data and update CellProfiler columns to match naming for JUMP

# In[8]:


# Load in labeled mitocheck data
label_df = pd.read_csv(label_data_path)

# Extract feature columns from the JUMP data filtered by phenotypic profiling model features
feature_cols = [col for col in label_df.columns if col.startswith("CP__")]
metadata_cols = [col for col in label_df.columns if col.startswith("Metadata_")]

# Filter df with only CP features and the metadata columns
mito_cp_df = label_df[
    ["Mitocheck_Phenotypic_Class"]
    + ["Cell_UUID"]
    + ["Location_Center_X"]
    + ["Location_Center_Y"]
    + metadata_cols
    + feature_cols
]

# change prefix for columns to match JUMP
mito_cp_df.columns = mito_cp_df.columns.str.replace("CP__", "Nuclei_")

print(mito_cp_df.shape)
mito_cp_df.head()


# ### Filter the mitocheck data

# In[9]:


# Load in labeled mitocheck data
label_df = pd.read_csv(label_data_path)

# Extract feature columns from the JUMP data filtered by phenotypic profiling model features
feature_cols = [col for col in label_df.columns if col.startswith("CP__")]

# Filter df with only CP features and the metadata column
mito_cp_df = label_df[["Mitocheck_Phenotypic_Class"] + feature_cols]

# change prefix for columns to match JUMP
mito_cp_df.columns = mito_cp_df.columns.str.replace("CP__", "Nuclei_")

# add data name column to separate between datasets
mito_cp_df.insert(0, "Metadata_data_name", "mitocheck")

# add data name column to separate between datasets
mito_cp_df.insert(2, "Metadata_Phenotypic_Value", 1)

# rename phenotypic class column from mito to match JUMP
mito_cp_df.rename(
    columns={"Mitocheck_Phenotypic_Class": "Metadata_Predicted_Class"}, inplace=True
)

# Find columns that are in the Mitocheck data but not the JUMP data (nuclei features only)
diff_columns = (
    pd.Index([col for col in mito_cp_df.columns if col.startswith("Nuclei_")])
    .difference(merged_prob_df.columns)
    .tolist()
)

# drop features that are not seen in JUMP to avoid merging errors
mito_cp_df = mito_cp_df.drop(columns=diff_columns)

print(mito_cp_df.shape)
mito_cp_df.head(2)


# ## Concat mitocheck and jump data (all nuclei features)

# In[10]:


# Concatenate the two DataFrames vertically
merged_mito_jump_df = pd.concat([mito_cp_df, jump_df], axis=0)

# Reset the index of the resulting DataFrame
merged_mito_jump_df.reset_index(drop=True, inplace=True)

# Add data frame to dictionary
df_dict["Mito_JUMP_all_features"] = merged_mito_jump_df

print(merged_mito_jump_df.shape)
merged_mito_jump_df.head(2)


# ## Only Zernike features

# In[11]:


# Extract metadata columns
metadata_cols = [
    col for col in merged_mito_jump_df.columns if col.startswith("Metadata")
]
# Extract feature columns
feature_cols = [col for col in merged_mito_jump_df.columns if col.startswith("Nuclei")]

# Filter feature columns for "Zernike"
zernike_feature_cols = [col for col in feature_cols if "Zernike" in col]

# Create a new DataFrame with metadata and filtered features
mito_jump_zernike_df = merged_mito_jump_df[metadata_cols + zernike_feature_cols]

# Add df to dictionary
df_dict["Mito_JUMP_zernike_features"] = mito_jump_zernike_df

print(mito_jump_zernike_df.shape)
mito_jump_zernike_df.head(2)


# ## Only AreaShape features

# In[12]:


# Extract metadata columns
metadata_cols = [
    col for col in merged_mito_jump_df.columns if col.startswith("Metadata")
]
# Extract feature columns
feature_cols = [col for col in merged_mito_jump_df.columns if col.startswith("Nuclei")]

# Filter feature columns for "Zernike"
areashape_feature_cols = [col for col in feature_cols if "AreaShape" in col]

# Create a new DataFrame with metadata and filtered features
mito_jump_areashape_df = merged_mito_jump_df[metadata_cols + areashape_feature_cols]

# Add df to dictionary
df_dict["Mito_JUMP_areashape_features"] = mito_jump_areashape_df

print(mito_jump_areashape_df.shape)
mito_jump_areashape_df.head(2)


# ## Generate UMAP coordinates for each of the data splits
# 
# 1. All Nuclei features from JUMP
# 2. All Nuclei features from Mitocheck + JUMP
# 3. Only Zernike features (AreaShape measurement) from Mitocheck + JUMP
# 4. Only AreaShape features from Mitocheck + JUMP

# In[13]:


# Set constants
umap_random_seed = 0
umap_n_components = 2

for data_name, df in df_dict.items():
    print(
        "Creating embeddings for",
        data_name,
        "and including the probabilities from the",
        model_type,
        "_".join(prob_path.stem.split("_")[:2]),
        "model",
    )
    # Make sure to reinitialize UMAP instance per plate
    umap_fit = umap.UMAP(random_state=umap_random_seed, n_components=umap_n_components)

    # Process df to separate features and metadata
    metadata_columns = [col for col in df.columns if col.startswith("Metadata")]
    feature_columns = [col for col in df.columns if not col.startswith("Metadata")]

    # Fit UMAP and convert to pandas DataFrame
    embeddings = pd.DataFrame(
        umap_fit.fit_transform(df.loc[:, feature_columns]),
        columns=[f"UMAP{x}" for x in range(0, umap_n_components)],
    )

    # Combine with metadata
    umap_with_metadata_df = pd.concat([df.loc[:, metadata_columns], embeddings], axis=1)

    if not data_name == "Only_JUMP_all_features":
        # Only include relevant metadata and UMAP coords (merged only)
        umap_with_metadata_df = umap_with_metadata_df[
            [
                "Metadata_data_name",
                "Metadata_Predicted_Class",
                "Metadata_Phenotypic_Value",
                "UMAP0",
                "UMAP1",
            ]
        ]

    # Make folder per data split
    model_dir = pathlib.Path(f"./{UMAP_results_dir}/{data_name}")
    model_dir.mkdir(exist_ok=True)

    # Generate output file and save
    output_umap_file = pathlib.Path(
        f"./{model_dir}/{data_name}_{model_type}_{'_'.join(prob_path.stem.split('_')[:2])}_model.tsv"
    )
    umap_with_metadata_df.to_csv(output_umap_file, index=False, sep="\t")

print(umap_with_metadata_df.shape)
umap_with_metadata_df.head()


# In[ ]:




