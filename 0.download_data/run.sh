#!/bin/bash
# Runs processing related to step 0.download_data
set -e

# convert all notebooks to python files into the nbconverted folder
conda run -n jump_sc jupyter nbconvert --to python \
    --output-dir=./0.download_data/nbconverted/ \
    ./0.download_data/*.ipynb

# download the jump manifest data
# use a subshell to keep existing code intact
(
cd ./0.download_data || exit
conda run -n jump_sc python ./nbconverted/0.generate_jump_dataset_manifest.py
)

# process the plate data using cytotable
conda run -n jump_sc python ./0.download_data/1.process_JUMP_plates_with_CytoTable.py

# download the images related to JUMP plate BR00117006
# use a subshell for relative pathing
(
cd ./0.download_data || exit
conda run -n jump_sc papermill ./2.download_images.ipynb ./2.download_images.ipynb -p plate_id BR00117006
)
