# Download JUMP-Target SQLite files from AWS

In this module, we download the SQLite files from [AWS](https://cellpainting-gallery.s3.amazonaws.com/index.html#cpg0000-jump-pilot/source_4/workspace/backend/2020_11_04_CPJUMP1/) with [aws-cli](https://github.com/aws/aws-cli) on Aug 10, 2023 using instructions provided from [JUMP Cell Painting Datasets](https://github.com/jump-cellpainting/datasets).
There are 51 plates from the pilot dataset (cpg0000), totalling 1.1 TB of storage from the SQLite files.

Firstly, we generate a manifest file in the [data folder](./data/) called [jump_dataset_location_manifest.csv](./data/jump_dataset_location_manifest.csv).
Afterwards, we process each plate using [CytoTable](https://github.com/cytomining/CytoTable).

Optionally, to download only the SQLite plates, please use the [download_from_aws.sh](./download_from_aws.sh) file, which contains the bash script that will download the files from the paths in the manifest.

Please see the notes from the main [`README.md` on processing this step](../README.md#running-code-from-this-project).

