# Single-cell Quality Control, Merge, Normalize, Feature Select, and Aggregate Single Cells

In this module, we perform five preprocessing steps on single-cell data generated from CytoTable outputs, using [pycytominer](https://github.com/cytomining/pycytominer/tree/main) for normalization, feature selection, and aggregation:

1. Perform single-cell quality control (QC) after CytoTable and before annotation/merging to remove low-quality cells.
2. Merge and annotate single-cell profiles from CytoTable outputs for downstream normalization and feature selection.
3. [Normalize](https://github.com/cytomining/pycytominer/blob/main/pycytominer/normalize.py) single cells using negative controls (for example, DMSO for compounds, no-target or intergenic-targeting sgRNAs for CRISPR, and weak-signature genes for ORF) as reference populations for standard scaling per plate.
4. [Feature select](https://github.com/cytomining/pycytominer/blob/main/pycytominer/feature_select.py) single-cell morphology data per plate using variance thresholding, correlation thresholding, and filtering columns containing NaNs or listed in the blocklist.
5. Aggregate both normalized and feature-selected single-cell morphology data to the well level.

## Run Single-cell Processing Pipeline

To process the data, run [process_data.sh](./process_data.sh), which converts notebooks to Python scripts in `nbconverted/` and runs QC-aware single-cell processing through merging/annotation, normalization, and feature selection; then run [aggregate_sc_data.sh](./aggregate_sc_data.sh) for well-level aggregation.

```bash
# Make sure you are in the 1.process_data directory
cd 1.process_data
# Process the data with steps 1-4
./process_data.sh
# Process the data with step 5
./aggregate_sc_data.sh
```
