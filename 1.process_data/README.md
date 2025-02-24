# Merge, normalize, feature select, and aggregate single cells with pycytominer

In this module, we perform four preprocessing steps on the SQLite files using [pycytominer](https://github.com/cytomining/pycytominer/tree/main):

1. Merge and annotate single cells from the SQLite file using the [pycytominer SingleCell class](https://github.com/cytomining/pycytominer/blob/main/pycytominer/cyto_utils/cells.py)
2. [Normalize](https://github.com/cytomining/pycytominer/blob/main/pycytominer/normalize.py) the single cells using the negative controls (e.g., DMSO for compound treatment, no-target or target intergenic region sgRNAs for crispr treatment, and genes with weak signatures in orf treatment) as reference for the standard scalar method per plate.
3. [Feature Select](https://github.com/cytomining/pycytominer/blob/main/pycytominer/feature_select.py) the single cell plate morphology data per plate.
4. [Aggregate](https://github.com/cytomining/pycytominer/blob/main/pycytominer/feature_select.py) both the normalized and feature selected single-cell morphology data to the well level.

## Run merging and normalization notebook

To process the data, run the [process_data.sh](./process_data.sh) file which will convert the notebook into a python file and run it from terminal.

```bash
# Make sure you are in the 1.process_data directory
cd 1.process_data
# Process the data with steps 1-3
./process_data
# Process the data with step 4
./aggregate_sc_data
```
