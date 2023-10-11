# JUMP-single-cell

## Data

In this repository, we apply the [phenotypic profiling model](https://github.com/WayScience/phenotypic_profiling_model), which predicts phenotypic class of single cells using nuclei features, on the [JUMP-Target pilot data](https://github.com/jump-cellpainting/JUMP-Target) from the [JUMP consortium](https://jump-cellpainting.broadinstitute.org/).

In this dataset, there are 51 plates that are associated with one of three treatment types:

- Compound
- CRISPR
- ORF

Each treatment has it's own platemap and metadata file that can be found in the [reference_plate_data](./reference_plate_data/) folder.
A barcode platemap is include which associates each plate to the correct platemap file.

There are a total of **20,959,860 single cells** between all plates.

To reproduce this project, please ensure adequate storage as the CellProfiler SQLite database files is approximately 1.1 TB large.

## Goal

Traditionally, image-based analyses aggregate single-cell features which removes outliers that could be interesting biology.
By predicting phenotypes for single-cells with the phenotypic profiling model, we hope to uncover patterns of biology that wouldn't be uncovered with the traditional methodology.

## Repository Structure

| Module | Purpose | Description |
| :---- | :----- | :---------- |
| [0.download_data](./0.download_data/) | Download JUMP-Target SQLite files | Download CellProfiler SQLite outputs for 51 plates from AWS |
| [1.process_data](./1.process_data/) | Process SQLite files | Using pycytominer, the SQLite outputs are converted to CSV features are merged into single-cells and normalized |
| [2.evaluate_data](./2.evaluate_data/) | Apply phenotypic profiling model | Phenotypic predictions are generated for single-cells using the phenotypic profiling model |
| [3.analyze_data](./3.analyze_data/) | Analyze phenotypic predictions | Multiple analyses are performed to validate the phenotypic predicted class for each treatment compared to control |
| [reference_plate_data](./reference_plate_data/) | Platemaps per treatment type | This folder holds the platemap files with metadata based on treatment and the barcode platemap file |

## Main environment

For all modules, we use one environment that includes all necessary packages. 

To create the environment from terminal, run the code line below:

```bash
# Make sure you are in the same directory as the environment file
conda env create -f environment.yml
```
