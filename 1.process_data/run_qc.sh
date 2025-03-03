#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the main conda environment
conda activate jump_sc

# Define the path to the parent folder
PARENT_FOLDER="/media/jenna/8TB-C/work/JUMP-single-cell/0.download_data/data/plates"

# Create an array of folder names (excluding files)
plates=($(find "$PARENT_FOLDER" -mindepth 1 -maxdepth 1 -type d -exec basename {} \;))

# Print the count of folders
echo "Number of plates found: ${#plates[@]}"

# Using papermill, run single cell quality control on all plates
for plate in "${plates[@]}"; do
    papermill \
    single_cell_qc.ipynb \
    single_cell_qc.ipynb \
    -p plate_id $plate
done

# Convert notebook to script
jupyter nbconvert --to=script --FilesWriter.build_directory=./nbconverted single_cell_qc.ipynb
