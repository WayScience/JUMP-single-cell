# Merge single cells and normalize using pycytominer

In this module, we perform two preprocessing steps on the SQLite files using [pycytominer](https://github.com/cytomining/pycytominer/tree/main):

1. Merge and annotate single cells from the SQLite file using the [pycytominer SingleCell class](https://github.com/cytomining/pycytominer/blob/main/pycytominer/cyto_utils/cells.py)
2. [Normalize](https://github.com/cytomining/pycytominer/blob/main/pycytominer/normalize.py) the single cells using the negative controls (e.g., DMSO treatment for compound treatment, no-target or target intergenic region sgRNAs for crispr treatment, and genes with weak signatures in orf treatment) as reference for the standard scalar method.

## Run merging and normalization notebook

To process the data, run the [process_data.sh](./process_data.sh) file which will convert the notebook into a python file and run it from terminal.

```bash
# Make sure you are in the 1.process_data directory
cd 1.process_data
# Run the notebook as a python script
source process_data.sh
```
