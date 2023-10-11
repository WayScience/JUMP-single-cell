# Download JUMP-Target SQLite files from AWS

In this module, we download the SQLite files from [AWS](https://cellpainting-gallery.s3.amazonaws.com/index.html#cpg0000-jump-pilot/source_4/workspace/backend/2020_11_04_CPJUMP1/).
There are 51 plates from the pilot dataset, totalling 1.1 TB of storage from the SQLite files.

Firstly, we generate a manifest file in the [data folder](./data/) called [jump_dataset_location_manifest.csv](./data/jump_dataset_location_manifest.csv).
Then, we use the [download_from_aws.sh](./download_from_aws.sh) file, which contains the bash script that will download the files from the paths in the manifest.
We call this file in a notebook to make it fully reproducible.

# Run the notebook to download the data

To generate the manifest and download the files, run the [download_data.sh](./download_data.sh) file which will convert the notebooks to python files and run them from terminal.

```bash
# Make sure you are in the 0.download_data directory
cd 0.download_data
# Run the notebooks as python scripts
source download_data.sh
```

