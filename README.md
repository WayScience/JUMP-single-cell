# JUMP-single-cell
Single cell analysis of the JUMP Cell Painting consortium data. Please ensure adequate storage as the sqlite plate data is approximately 1.1 TB large.

## 0.download_data
This folder contains the code and metadata file to download the plate data from aws. For more information on how the plate paths were generated please visit the `create_download_paths` file for more information. The `download_jump_data` code was not reran for the sake of time and storage.

To download the data, first run `create_download_paths.ipynb`, to generate the paths data, then run `download_jump_data.ipynb` to download the plate data.

## 1.process_data
In this step, the data was merged into single cell data using pycytominer, and the reference plate data located in the `reference_plate_data` folder. Then the plate data was normalized by pycytominer and converted to parquet files.
