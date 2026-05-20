# Merge, Normalize, Feature Select, and Aggregate Single Cells with pycytominer

In this module, we perform four preprocessing steps on SQLite files using [pycytominer](https://github.com/cytomining/pycytominer/tree/main):

1. Merge and annotate single cells from the SQLite file using the [pycytominer SingleCell class](https://github.com/cytomining/pycytominer/blob/main/pycytominer/cyto_utils/cells.py)
2. [Normalize](https://github.com/cytomining/pycytominer/blob/main/pycytominer/normalize.py) single cells using negative controls (for example, DMSO for compounds, no-target or intergenic-targeting sgRNAs for CRISPR, and weak-signature genes for ORF) as reference populations for standard scaling per plate.
3. [Feature select](https://github.com/cytomining/pycytominer/blob/main/pycytominer/feature_select.py) single-cell morphology data per plate using variance thresholding, correlation thresholding, and filtering columns containing NaNs or listed in the blocklist.
4. Aggregate both normalized and feature-selected single-cell morphology data to the well level.

## Run Merging and Normalization Notebook

To process the data, run [process_data.sh](./process_data.sh), which converts notebooks to Python scripts in `nbconverted/` and runs normalization plus feature selection.

```bash
# Make sure you are in the 1.process_data directory
cd 1.process_data
# Process the data with steps 1-3
./process_data.sh
# Process the data with step 4
./aggregate_sc_data.sh
```
