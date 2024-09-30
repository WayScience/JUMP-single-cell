[![DOI](https://zenodo.org/badge/625612264.svg)](https://zenodo.org/doi/10.5281/zenodo.10815000)

# JUMP-single-cell

## Data

In this repository, we apply the [phenotypic profiling model](https://github.com/WayScience/phenotypic_profiling_model), which predicts phenotypic class of single cells using nuclei features, to the [JUMP-Target pilot data](https://github.com/jump-cellpainting/JUMP-Target) from the [JUMP consortium](https://jump-cellpainting.broadinstitute.org/).

In this dataset, there are 51 plates with one of three perturbation types (Clustered Regularly Interspaced Short Palindromic Repeats [CRISPR], Open Reading Frame [ORF], and Compound) for two cell lines (A549 and U2OS).

Each perturbation type has it's own platemap and metadata file that can be found in the [reference_plate_data](./reference_plate_data/) folder.
A barcode platemap is include which associates each plate to the correct platemap file.

We segment a total of **20,959,860 single cells** in all plates.

To reproduce this project, please ensure adequate storage as the CellProfiler SQLite database files are approximately 1.1 TB.

## Goal

Traditional image-based profiling pipelines aggregate single-cells into well-level profiles.
While, this process removes outliers that might dampen signal, it also removes potentially interesting biologically-meaningful heterogeneity.

By predicting single-cell phenotypes with our phenotypic profiling model, we hope to uncover important patterns of biology that would be missed with the traditional methodology.
Specifically, the benefits of single-cell phenotyping include:

- Granular phenotypic mechanisms of perturbations regarding (A) the impact perturbations have on a specific phenotype (e.g., disrupting mitosis) and (B) impact on phenotype prevalence (e.g., a gene knockout that causes apoptosis or stalls cells in a specific cell cycle phase).
-  Filter and/or combine cells of the same phenotypic class to purify and/or improve the traditional image-based profiling pipeline.
- Adding knowledge to specific combinations of morphology features allows for self-referential interpretation, without the need for database signature lookup or other guilt-by-association methods.
- When combined with different experimental designs (e.g., targeted fluorescence marker), we can test specific hypotheses regarding single-cell phenotype distributions (and other important hypotheses that would otherwise be impossible without single-cell phenotypes).

## Repository Structure

| Module | Purpose | Description |
| :---- | :----- | :---------- |
| [0.download_data](./0.download_data/) | Download JUMP-Target SQLite files | We downloaded the CellProfiler SQLite outputs for 51 plates from AWS |
| [1.process_data](./1.process_data/) | Process SQLite files | We use pycytominer on the SQLite outputs to merge single-cells and normalize features |
| [2.evaluate_data](./2.evaluate_data/) | Apply phenotypic profiling model | We generate phenotypic predictions for single-cells using the phenotypic profiling model |
| [3.analyze_data](./3.analyze_data/) | Analyze phenotypic predictions | We perform multiple analyses to validate the phenotypic predicted class for each perturbation compared to control |
| [reference_plate_data](./reference_plate_data/) | Platemaps per perturbation type | This folder holds the platemap files with metadata based on perturbation type and the barcode platemap file |

## Development

We use a [`justfile`](justfile) to specify [`just`](https://github.com/casey/just) commands for use with this project.
Please see [`just` installation details](https://just.systems/man/en/packages.html) for configuration on your system.

### Environment

For all modules, we use conda environments that includes all necessary packages.

To create the environment from terminal, run the code line below:

```bash
# Make sure you are in the same directory as the environment file
conda env create -f environment.yml
```

Alternatively, use the following `just` command

```bash
just setup-conda-envs
```
