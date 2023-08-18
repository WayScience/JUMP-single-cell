#!/usr/bin/env python
# coding: utf-8

# # Compare phenotypic expression among treatments with volcano plot visualizations
# We compare phenotypic expression for each (phenotype, statistical test, model type, treatment type) combination

# In[1]:


import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


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


# ## Define the input dataframe from the parquet path

# In[3]:


drive_path = f"{root_dir}/big_drive"
compdf = pd.read_parquet(f"{drive_path}/statistical_test_comparisons/comparison_results.parquet")


# ## Define and create output path

# In[4]:


output_path = pathlib.Path("figures")

output_path.mkdir(parents=True, exist_ok=True)


# In[5]:


# Bernoulli adjustment
alpha = 0.05 / len(compdf)

# Remove the zero values after the p-value adjustment
compdf = compdf.loc[compdf["p_value"] > 0]
significance_threshold = -np.log10(alpha)

# Define the unique groups to plot
unique_comparisons = set(zip(compdf["phenotype"], compdf["treatment_type"], compdf["model_type"], compdf["statistical_test"]))

# Specify colors according to categories
colors = {
'x_below_threshold': 'green',        # Color for x < 0 and y > significance_threshold
'x_above_threshold': 'red',       # Color for x > 0 and y > significance_threshold
'y_below_threshold': 'blue'          # Color for y < significance_threshold
}

# Convert the p-values to negative log p-values
compdf["neg_log_p_value"] = -np.log10(compdf["p_value"])

# Specify the (x,y) thresholds for coloring the plots
compdf["category"] = compdf.apply(lambda row:
    'x_below_threshold' if row['comparison_metric_value'] < 0 and row['neg_log_p_value'] > significance_threshold else
    'x_above_threshold' if row['comparison_metric_value'] > 0 and row['neg_log_p_value'] > significance_threshold else
    'y_below_threshold',
    axis=1
)

for comp in unique_comparisons:

    fig, ax = plt.subplots(figsize=(15, 10))
    groupdf = compdf.copy()

    # Seperate the croups we are intersted in plotting
    groupdf = groupdf.loc[((groupdf["phenotype"] == comp[0]) & (groupdf["treatment_type"] == comp[1]) & (groupdf["model_type"] == comp[2]) & (groupdf["statistical_test"] == comp[3]))]

    # Create the scatter plot with size and color differentiation
    sns.scatterplot(
        data=groupdf,
        x="comparison_metric_value",
        y="neg_log_p_value",
        hue="category",
        palette=colors,
        legend=False,
        ax = ax
    )

    # Add threshold lines
    plt.axhline(
        significance_threshold,
        color="black",
        linestyle="--",
        label="Significance Threshold",
    )

    # Get the name of the statistical test and apply formating
    f_test_title = comp[3].replace("_", " ")
    f_test_title = f_test_title.title()

    # Set plot labels and title
    plt.xlabel("median")
    plt.ylabel("-log10(p-value)")
    plt.title(f"{f_test_title} tests of Treatment probabilities for phenotype {comp[0].upper()} and treatment type {comp[1].upper()} compared to DMSO")

    # Make the output directory if it doesn't exist
    fig_path = output_path / f"{comp[1]}/{comp[0]}/{comp[2]}/{comp[3]}"
    fig_path.mkdir(parents=True, exist_ok=True)

    # Save the plot
    plt.savefig(f"{fig_path}/{comp[3]}_volcano_{comp[0]}_{comp[1]}.png")
    plt.close(fig)

