# JUMP-single-cell

Single cell analysis of the JUMP Cell Painting consortium data.
Please ensure adequate storage as the sqlite plate data is approximately 1.1 TB large.

## 0.download_data

This folder contains the code and metadata file to download the plate data from aws.
For more information on how the plate paths were generated please review the `0.generate_jump_dataset_manifest.ipynb` file.

To download the data, first run `0.generate_jump_dataset_manifest.ipynb`, to generate the paths data, then run `1.download_jump_single_cell_profiles.ipynb` to download the plate data.

## 1.process_data

In this step, we merged the single cell data using pycytominer, and the reference plate data located in the `reference_plate_data` folder in the root of the git directory.
The metadata files in this folder can be located by following this aws link:
`https://cellpainting-gallery.s3.amazonaws.com/index.html#cpg0000-jump-pilot/source_4/workspace/metadata/external_metadata/`

The platemaps files in this folder can be found using this aws link:
`https://cellpainting-gallery.s3.amazonaws.com/index.html#cpg0000-jump-pilot/source_4/workspace/metadata/platemaps/2020_11_04_CPJUMP1/platemap/`

Similarly the barcode file `barcode_platemap.csv` came from dropbox.

After merging the single cells, each of the features of the plate data were normalized by pycytominer and converted to parquet files.

## 2.evaluate_data

In this step, we perform inferencing with the pre-trained shuffled and unshuffled logistic regression models from the phenotypic profiling repository `https://github.com/WayScience/phenotypic_profiling_model/tree/main`.
We generate predicted probabilities for each cell expressing one of the fifteen possible phenotypes.
This data in addition to the other single cell metadata is stored as a parquet file.
