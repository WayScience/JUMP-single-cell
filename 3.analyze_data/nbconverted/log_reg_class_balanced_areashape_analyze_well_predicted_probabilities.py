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
big_drive_path = f"{root_dir}/big_drive"
sqlite_data_path = f"{big_drive_path}/sc_data"
ref_path = f"{root_dir}/reference_plate_data"
proba_path = f"{big_drive_path}/class_balanced_log_reg_probability_sc_data/greg_areashape_log_reg_class_balanced_probabilities.parquet"

bar_plate_path = f"{ref_path}/barcode_platemap.csv"
sig_test_path = "utils/significance_testing"

# Define barcode platemap dataframe
barcode_platemapdf = pd.read_csv(bar_plate_path)

# Define the probabilities dataframe
probadf = pd.read_parquet(proba_path)

# Metadata and platemap paths and the name of the treatment_columns for each treatment type
treatment_paths = {"compound":  # Name of the treatment type
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


comparison_results_output_filename = "class_balanced_well_log_reg_areashape_greg_model_comparisons.parquet"
output_path = pathlib.Path("class_balanced_well_log_reg_comparison_results")
output_path.mkdir(parents=True, exist_ok=True)

# Fill blank broad samples in the broad_sample column with DMSO.
# These samples are represented as DMSO in the platemap, but as nans when loaded as a DataFrame
treatment_paths["compound"]["platemap"]["broad_sample"].fillna("DMSO", inplace=True)
treatment_paths["compound"]["metadata"]["broad_sample"].fillna("DMSO", inplace=True)


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


# ## Defining tests and aggregation metric names

# In[6]:


# Create a dictionary where the keys represent the name of the comparison or test, and the values are dictionaries
# the subdictionaries refer to the wrapper function for creating the comparison, and the metric name of the comparison being made
comp_functions = {"ks_test":
                  {"statistical_test_function": perform_ks_test,
                   "comparison_metric": "ks_statistic"}
                  }


# In[7]:


treatments = sig_test.get_treatment_comparison(comp_functions, treatment_paths, probadf, barcode_platemapdf)


# ## Save the output of the treatment

# In[8]:


treatments = pd.DataFrame(treatments)
treatments.to_parquet(output_path / comparison_results_output_filename)

