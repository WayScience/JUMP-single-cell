# Download JUMP-Target SQLite Files from AWS

In this module, we download SQLite files from [AWS](https://cellpainting-gallery.s3.amazonaws.com/index.html#cpg0000-jump-pilot/source_4/workspace/backend/2020_11_04_CPJUMP1/) with [aws-cli](https://github.com/aws/aws-cli), following instructions from [JUMP Cell Painting Datasets](https://github.com/jump-cellpainting/datasets).
There are 51 plates from the pilot dataset (`cpg0000`), totaling about 1.1 TB of SQLite files.

First, we generate a manifest file in the [data folder](./data/) called [jump_dataset_location_manifest.csv](./data/jump_dataset_location_manifest.csv).
Afterward, we process each plate using [CytoTable](https://github.com/cytomining/CytoTable).

The module entrypoint is [run.sh](./run.sh), which runs manifest generation, CytoTable plate processing, and image-download notebook execution.

Optionally, to download only the SQLite plates, use [download_from_aws.sh](./download_from_aws.sh), which downloads files from paths in the manifest.

See the main [`README.md` section on running code](../README.md#running-code-from-this-project) for step-level execution details.
