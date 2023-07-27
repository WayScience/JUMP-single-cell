# JUMP-single-cell
Single cell analysis of the JUMP Cell Painting consortium data. Please ensure adequate storage as the sqlite plate data is approximately 1.1 TB large.

## 0.download_data
This folder contains the code and metadata file to download the plate data from aws. The metadata contains the following information:
- jump_dataset.csv
    - This dataset contains the aws s3 links to each of the sqlite plate files, speficied as rows. These links were acquired by modifying the source path of the sqlite files by:
        - Replacing the prefix `https://` with `s3://`
        - Removing the string `.s3.amazonaws.com`
        - Replacing the plate names with the corresponding plate names, which start with `BR` in this case, such as `BR00116991`

## 1.process_data
In this step, the data was merged into single cell data using pycytominer, and the reference plate data located in the `reference_plate_data` folder. Then the plate data was normalized by pycytominer and converted to parquet files.
