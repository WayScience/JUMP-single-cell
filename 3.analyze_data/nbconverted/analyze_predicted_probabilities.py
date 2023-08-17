#!/usr/bin/env python
# coding: utf-8

# # Test treatement probabilities for each phenotype

# In[1]:


import pathlib
import sys

import numpy as np
import pandas as pd
from scikit_posthocs import posthoc_dunn
from scipy.stats import mannwhitneyu

# Import significance test utils
sys.path.append("utils")
import significance_testing as sig_test


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
proba_path = f"{big_drive_path}/probability_sc_data/model_probabilities.parquet"
sig_test_path = "utils/significance_testing"

# Define the probabilities dataframe
probadf = pd.read_parquet(proba_path)

# Metadata and platemap paths and the name of the treatment_columns for each treatment type
treatment_paths = {"compound":
               {"metadata": pd.read_csv(f"{ref_path}/JUMP-Target-1_compound_metadata_targets.tsv", sep="\t"), "platemap": pd.read_csv(f"{ref_path}/JUMP-Target-1_compound_platemap.txt", sep="\t"), "treatment_column": "pert_iname"},
               "crispr":
               {"metadata": pd.read_csv(f"{ref_path}/JUMP-Target-1_crispr_metadata.tsv", sep="\t"), "platemap": pd.read_csv(f"{ref_path}/JUMP-Target-1_crispr_platemap.txt", sep="\t"), "treatment_column": "target_sequence"},
               "orf":
               {"metadata": pd.read_csv(f"{ref_path}/JUMP-Target-1_orf_metadata.tsv", sep="\t"), "platemap": pd.read_csv(f"{ref_path}/JUMP-Target-1_orf_platemap.txt", sep="\t"), "treatment_column": "gene"}}


# ## Define and create the output paths

# In[4]:


comparison_results_output_filename = "comparison_results.parquet"
output_path = pathlib.Path(f"{big_drive_path}/statistical_test_comparisons")
output_path.mkdir(parents=True, exist_ok=True)

# Fill blank broad samples in the broad_sample column with DMSO.
# These samples are represented as DMSO in the platemap, but as nans when loaded as a DataFrame
treatment_paths["compound"]["platemap"]["broad_sample"].fillna("DMSO", inplace=True)


# ## Mann-whitney U wrapper function

# In[5]:


def perform_mannwhitneyu_median(_dmso_probs, _treatment_probs):
    """
    Parameters
    ----------
    _dmso_probs: Pandas Series
        The down-sampled predicted probilities of DMSO for a treatment type and phenotype.

    _treatment_probs: Pandas Series
        The predicted probabilities of the treatment.

    Returns
    -------
    A zipped object which represents can be referenced by p_value and a comparison_metric_value, which are later on represented in the resulting dictionary.
    """

    test_result = mannwhitneyu(_dmso_probs, _treatment_probs, alternative="two-sided")
    med_diff = _treatment_probs.median() - _dmso_probs.median()
    return zip(["comparison_metric_value", "p_value"], [med_diff, test_result[1]])


# ## Dunn wrapper function

# In[6]:


def perform_dunn_median(_dmso_probs, _treatment_probs):
    """
    Parameters
    import numpy as np
    ----------
    _dmso_probs: Pandas Series
        The down-sampled predicted probilities of DMSO for a treatment type and phenotype.

    _treatment_probs: Pandas Series
        The predicted probabilities of the treatment.

    Returns
    -------
    A zipped object which represents can be referenced by p_value and a comparison_metric_value, which are later on represented in the resulting dictionary.
    """
    data = {
        'probs': np.hstack((_dmso_probs.to_numpy(), _treatment_probs.to_numpy())),
        'group': ['DMSO'] * len(_dmso_probs) + ['Treatment'] * len(_treatment_probs)
    }

    df = pd.DataFrame(data)
    p_value = posthoc_dunn(df, val_col="probs", group_col="group")
    med_diff = _treatment_probs.median() - _dmso_probs.median()
    return zip(["comparison_metric_value", "p_value"], [med_diff, p_value.loc["DMSO", "Treatment"]])


# ## Defining tests and aggregation metric names

# In[7]:


comp_functions = {"dunn_test":
                  {"statistical_test_function": perform_dunn_median,
                   "comparison_metric": "median_difference"},
                  "mann_whitney_u":
                  {"statistical_test_function": perform_mannwhitneyu_median,
                   "comparison_metric": "median_difference"}}


# In[8]:


treatments = sig_test.get_treatment_comparison(comp_functions, treatment_paths, probadf)


# ## Save the comparisons data

# In[9]:


treatments = pd.DataFrame(treatments)
treatments.to_parquet(output_path / comparison_results_output_filename)

