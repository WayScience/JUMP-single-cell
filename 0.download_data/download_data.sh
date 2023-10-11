#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash

# activate the main conda environment
conda activate jump_sc

# convert all notebooks to python files into the nbconverted folder
jupyter nbconvert --to python --output-dir=nbconverted/ *.ipynb

# run the python scripts in order
python nbconverted/0.generate_jump_dataset_manifest.py
python nbconverted/1.download_jump_single_cell_profiles.py