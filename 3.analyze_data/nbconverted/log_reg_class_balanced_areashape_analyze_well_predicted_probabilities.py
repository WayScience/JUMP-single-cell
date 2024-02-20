#!/usr/bin/env python
# coding: utf-8

# # Compare Well Treatements
# We compare the treatments in each well using cell treatment probabilities and negative control probabilities for each phenotype.
# This comparison is accomplished with a KS Test.

# In[1]:


import pathlib
import sys

import pandas as pd
from scipy.stats import kstest

# Import significance test utils
sys.path.append("utils")
import well_significance_testing as sig_test


# ## Find the root of the git repo on the host system

# In[2]:


# Get the current working directory
cwd = pathlib.Path.cwd()

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


# ## Input Paths

# In[3]:


# Input paths

# Path to the drive storing the data
big_drive_path = f"{root_dir}/big_drive"

# Path to the reference plate manifest data
ref_path = f"{root_dir}/reference_plate_data"

# Path to the plate probability data
proba_path = pathlib.Path(f"{big_drive_path}/class_balanced_log_reg_probability_sc_data")

# Paths of each plate file
proba_plate_paths = proba_path.glob("*.parquet")

# Define barcode platemap dataframe
barcode_platemapdf = pd.read_csv(f"{ref_path}/barcode_platemap.csv")

# Define experiment metadata dataframe
exmetadf = pd.read_csv(f"{ref_path}/experiment-metadata.tsv", sep="\t")

# Metadata and platemap paths and the name of the treatment_columns for each treatment type
treatment_data = {
"compound":  # Name of the treatment type
    {"metadata": pd.read_csv(f"{ref_path}/JUMP-Target-1_compound_metadata_targets.tsv", sep="\t"),  # Metadata
     "platemap": pd.read_csv(f"{ref_path}/JUMP-Target-1_compound_platemap.txt", sep="\t"),  # Platemap data
     "treatment_column": "pert_iname",  # Name of the treatment column in the metadata
     "Plate_Map_Name": "JUMP-Target-1_compound_platemap"},  # Name of the plate for iterating through treatment types
"crispr":
    {"metadata": pd.read_csv(f"{ref_path}/JUMP-Target-1_crispr_metadata.tsv", sep="\t"),
     "platemap": pd.read_csv(f"{ref_path}/JUMP-Target-1_crispr_platemap.txt", sep="\t"),
     "treatment_column": "gene",
     "Plate_Map_Name": "JUMP-Target-1_crispr_platemap"},
"orf":
    {"metadata": pd.read_csv(f"{ref_path}/JUMP-Target-1_orf_metadata.tsv", sep="\t"),
     "platemap": pd.read_csv(f"{ref_path}/JUMP-Target-1_orf_platemap.txt", sep="\t"),
     "treatment_column": "gene",
     "Plate_Map_Name": "JUMP-Target-1_orf_platemap"}
}


# ## Define and create the output paths

# In[4]:


comparison_results_output_filename = "class_balanced_well_log_reg_areashape_model_comparisons.parquet"
output_path = pathlib.Path("class_balanced_well_log_reg_comparison_results")
output_path.mkdir(parents=True, exist_ok=True)


# ## KS test wrapper function

# In[5]:


def perform_ks_test(_dmso_probs, _treatment_probs):
    """
    Parameters
    ----------
    _dmso_probs: pandas.Series
        The down-sampled predicted probilities of DMSO for a treatment type and phenotype.

    _treatment_probs: pandas.Series
        The predicted probabilities of the treatment.

    Returns
    -------
    A zipped object which represents can be referenced by p_value and a comparison_metric_value, which are later on represented in the resulting dictionary.
    """
    stat, p_value = kstest(_dmso_probs, _treatment_probs, alternative="two-sided")
    return zip(["comparison_metric_value", "p_value"], [stat, p_value])


# # Process the data

# ## Combine barcode platemap and experiment metadata

# In[6]:


barcode_platemapdf = pd.merge(barcode_platemapdf, exmetadf, how="inner", on=["Assay_Plate_Barcode", "Plate_Map_Name"])


# ## Combine the model probabilty and plate data

# In[7]:


def combine_meta(probadf):
    """
    Parameters
    ----------
    probadf: pandas.Dataframe
        The phenotypic probability data of a given plate

    Returns
    -------
    The combined probability and plate metadata
    """
    # Columns names to drop after merging data
    drop_cols = ["Assay_Plate_Barcode", "well_position"]

    # Retrieve the data that correspond to the plate names, where the plate names correspond to the treatment type
    filtered_probadf = pd.merge(probadf, barcode_platemapdf, how="inner", left_on="Metadata_Plate", right_on="Assay_Plate_Barcode")

    filtered_probadf.rename(columns={"Plate_Map_Name": "treatment_type"}, inplace=True)

    # Merge the metadata and platemaps for each type of treatment
    broaddfs = {ttype: pd.merge(treatment_data[ttype]["metadata"], treatment_data[ttype]["platemap"], how="inner", on="broad_sample") for ttype in treatment_data.keys()}

    # Iterate through each type of treatment
    for ttype in broaddfs.keys():

        # Rename the treatment columns
        broaddfs[ttype].rename(columns={treatment_data[ttype]["treatment_column"]: "treatment"}, inplace=True)

        # Set the type of treatment
        broaddfs[ttype]["treatment_type"] = ttype

        # Change the treatment type data values
        filtered_probadf["treatment_type"].replace({treatment_data[ttype]["Plate_Map_Name"]: ttype}, inplace=True)

    combined_broaddf = pd.concat(broaddfs.values(), axis=0, ignore_index=True)

    # Combine the probability and treatment data using the well
    common_broaddf = pd.merge(filtered_probadf, combined_broaddf, how="inner", left_on=["Metadata_Well", "treatment_type"], right_on=["well_position", "treatment_type"])

    # Drop redundant columns from the merge operations
    common_broaddf.drop(columns=drop_cols, inplace=True)

    return common_broaddf


# In[8]:


# Fill blank broad samples in the broad_sample column with DMSO.
# These samples are represented as DMSO in the platemap, but as nans when loaded as a DataFrame
treatment_data["compound"]["platemap"]["broad_sample"].fillna("DMSO", inplace=True)
treatment_data["compound"]["metadata"]["broad_sample"].fillna("DMSO", inplace=True)


# ## Defining tests and aggregation metric names

# In[9]:


# Create a dictionary where the keys represent the name of the comparison or test, and the values are dictionaries
# the subdictionaries refer to the wrapper function for creating the comparison, and the metric name of the comparison being made
comp_functions = {"ks_test":  # Name of the test to perform
                  {"statistical_test_function": perform_ks_test,  # The function for making comparisons
                   "comparison_metric": "ks_statistic"}  # The name of the comparison metric
                  }


# ## Compare treatments and negative controls

# In[10]:


# Define columns to group by
filt_cols = ['Metadata_Plate', 'treatment', 'Metadata_model_type', 'treatment_type', 'Metadata_Well', 'Cell_type']

# Columns of interest which should also be tracked
tracked_cols = ["Time"]

# Store phenotype column names
phenotype_cols = None

# Store comparison data
comparisons = None

# Compute comparisons by iterating through each plate
for proba_path in list(proba_plate_paths):

    # Combine the probability data with the plate manifest files
    common_broaddf = combine_meta(pd.read_parquet(proba_path))

    # Define the phenotypes only once
    if phenotype_cols is None:
        # Define phenotype columns
        phenotype_cols = common_broaddf.loc[:, "ADCCM":"SmallIrregular"].columns.tolist()

    # Compare the treatments and controls of each plate
    plate_comparison = sig_test.get_treatment_comparison(
        comp_functions,
        common_broaddf.loc[common_broaddf["control_type"] != "negcon"],
        common_broaddf.loc[common_broaddf["control_type"] == "negcon"],
        phenotype_cols,
        filt_cols,
        tracked_cols
    )

    # Define the comparisons data structure for the first time
    if comparisons is None:
        comparisons = plate_comparison

    # If the comparisons data structure is already defined append to the existing data structure
    else:
        for col, col_val in plate_comparison.items():
            comparisons[col] += col_val


# ## Save the output of the treatment

# In[11]:


comparisons = pd.DataFrame(comparisons)
comparisons.to_parquet(output_path / comparison_results_output_filename)

