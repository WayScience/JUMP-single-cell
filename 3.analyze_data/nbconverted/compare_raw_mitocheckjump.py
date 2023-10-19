#!/usr/bin/env python
# coding: utf-8

# ## Compare raw features between mitocheck and jump

# In[1]:


import pathlib
import random
import warnings
import numpy as np
import pandas as pd
from scipy import stats

from pycytominer.cyto_utils import infer_cp_features


# In[2]:


# Ignore divide by zero error
warnings.simplefilter("ignore", category=RuntimeWarning)


# In[3]:


def drop_prefix(feature_list, delimiter="_"):
    """
    Split feature list and join back by delimiter
    """
    return [delimiter.join(x.split(delimiter)[1:]).strip(delimiter) for x in feature_list]


def compare_dataset_features(
    mitocheck_data,
    jump_data,
    features,
    random_seed=123,
    jump_random_sample_n=0,
    jump_random_wells=[],
    mitocheck_phenotypes=[]
):
    """
    Compare feature space of mitocheck and jump data via univariate non-parametric tests
    """
    random.seed(random_seed)

    # Subset the input datasets
    if len(jump_random_wells) > 0:
        jump_data = jump_data.query("Metadata_Well in @jump_random_wells")
    if jump_random_sample_n > 0:
        jump_data = jump_data.sample(n=jump_random_sample_n)

    if len(mitocheck_phenotypes) > 0:
        mitocheck_data = mitocheck_data.query("Mitocheck_Phenotypic_Class in @mitocheck_phenotypes")
    
    full_results = []
    for feature in features:
        subset_jump_feature = f"Nuclei_{feature}"
        subset_mitocheck_feature = f"CP__{feature}"
    
        jump_distribution = jump_data.loc[:, subset_jump_feature]
        mitocheck_distribution = mitocheck_data.loc[:, subset_mitocheck_feature]
    
        results = stats.kstest(mitocheck_distribution, jump_distribution)
        ks_stat = results.statistic
        ks_pval = results.pvalue
        
        mitocheck_mean = np.mean(mitocheck_distribution)
        mitocheck_var = np.var(mitocheck_distribution)
        jump_mean = np.mean(jump_distribution)
        jump_var = np.var(jump_distribution)
        full_results.append(
            [feature, ks_stat, ks_pval, mitocheck_mean, mitocheck_var, jump_mean, jump_var]
        )
    
    full_results_df = (
        pd.DataFrame(
            full_results,
            columns=[
                "feature",
                "ks_stat",
                "ks_pval",
                "mitocheck_mean",
                "mitocheck_variance",
                "jump_mean",
                "jump_variance"
            ]
        )
        .sort_values(by="ks_stat", ascending=False)
        .reset_index(drop=True)
    )
    
    full_results_df = full_results_df.assign(
        neg_log_p = -np.log(full_results_df.ks_pval),
        random_seed=random_seed
    )
    return full_results_df


# In[4]:


# We ran this notebook twice; with normalized_data = True and again = False
normalized_data = False
n_permutations = 1000


# In[5]:


# Setup file i/o
jump_dir = "example_feature_data"
if normalized_data:
    mitocheck_dir = pathlib.Path("../../mitocheck_data/3.normalize_data/normalized_data/")
    jump_file = pathlib.Path(jump_dir, "BR00116991_normalized_sc.parquet")
    output_file = "ks_test_differences_normalized.tsv.gz"
else:
    mitocheck_dir = pathlib.Path("../../mitocheck_data/2.format_training_data/results/")
    jump_file = pathlib.Path(jump_dir, "BR00116991_merged_sc.parquet")
    output_file = "ks_test_differences_raw.tsv.gz"

mitocheck_raw_file = pathlib.Path(mitocheck_dir, "training_data.csv.gz")
output_file = pathlib.Path("results", output_file)


# In[6]:


# Load full mitocheck dataset
mitocheck_df = pd.read_csv(mitocheck_raw_file, index_col=0)

# Obtain important feature data
mitocheck_metadata = ["Mitocheck_Phenotypic_Class", "Cell_UUID", "Location_Center_X", "Location_Center_Y"] +\
    mitocheck_df.columns[mitocheck_df.columns.str.contains("Metadata")].tolist()
mitocheck_cp_features = mitocheck_df.columns[mitocheck_df.columns.str.startswith("CP")].tolist()

print(mitocheck_df.shape)
mitocheck_df.head(2)


# In[7]:


# Set constant to match mitocheck n
jump_random_sample_n = mitocheck_df.shape[0]


# In[8]:


# Load full JUMP data\
jump_df = pd.read_parquet(jump_file)

# Obtain important feature information
jump_metadata = infer_cp_features(jump_df, metadata=True)
jump_cp_features = infer_cp_features(jump_df, compartments="Nuclei")

print(jump_df.shape)
jump_df.head(2)


# In[9]:


# Get common features
jump_no_prefix_features = drop_prefix(jump_cp_features)
mitocheck_no_prefix_features = drop_prefix(mitocheck_cp_features)

all_features = set(jump_no_prefix_features + mitocheck_no_prefix_features)

# Create dataframe for feature lookup
feature_membership = []
for feature in all_features:
    in_jump = feature in jump_no_prefix_features
    in_mitocheck = feature in mitocheck_no_prefix_features
    feature_membership.append([feature, in_jump, in_mitocheck])

feature_membership_df = pd.DataFrame(feature_membership, columns=["feature", "in_jump", "in_mitocheck"])

feature_membership_df = (
    feature_membership_df
    .assign(in_both=(feature_membership_df.in_jump & feature_membership_df.in_mitocheck))
    .sort_values(by="in_both", ascending=False)
    .reset_index(drop=True)
)

print(feature_membership_df.shape)
feature_membership_df.head(2)


# In[10]:


# What about common features?
common_features = feature_membership_df.query("in_both").feature.tolist()
print(len(common_features))


# In[11]:


# Perform a KS-test in different random samples
random_seeds = [random.randint(0, 1000000) for x in range(n_permutations)]

all_results = []
counter = 0
for seed in random_seeds:
    
    counter += 1
    if counter % 100 == 0:
        print(f"Progress: {counter}/{len(random_seeds)} permutations complete.")
        
    result = compare_dataset_features(
        mitocheck_data=mitocheck_df,
        jump_data=jump_df,
        features=common_features,
        random_seed=seed,
        jump_random_sample_n=jump_random_sample_n,
        jump_random_wells=[],
        mitocheck_phenotypes=[]
    )
    all_results.append(result)


# In[12]:


# Output to file
(
    pd.concat(all_results)
    .sort_values(by="ks_pval")
    .reset_index(drop=True)
    .to_csv(output_file, sep="\t", index=False)
)

