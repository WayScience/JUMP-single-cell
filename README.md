# JUMP-single-cell
Single cell analysis of the JUMP Cell Painting consortium data.
Please ensure adequate storage as the sqlite plate data is approximately 1.1 TB large.

## 0.download_data
This folder contains the code and metadata file to download the plate data from aws.
For more information on how the plate paths were generated please visit the `create_download_paths` file for more information.
The `download_jump_data` code was not reran for the sake of time and storage.

To download the data, first run `create_download_paths.ipynb`, to generate the paths data, then run `download_jump_data.ipynb` to download the plate data.

## 1.process_data
In this step, the data was merged into single cell data using pycytominer, and the reference plate data located in the `reference_plate_data` folder.
The metadata files in this folder can be located by following this aws link:
`https://cellpainting-gallery.s3.amazonaws.com/index.html#cpg0000-jump-pilot/source_4/workspace/metadata/external_metadata/`

The platemaps for this folder can be found from this aws link:
https://cellpainting-gallery.s3.amazonaws.com/index.html#cpg0000-jump-pilot/source_4/workspace/metadata/platemaps/2020_11_04_CPJUMP1/platemap/

Similarly the barcode file came from dropbox.

After merging the single cells, each of the features of the plate data were normalized by pycytominer and converted to parquet files.
