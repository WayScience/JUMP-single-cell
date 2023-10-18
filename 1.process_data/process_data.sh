#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash

# activate the main conda environment
conda activate jump_sc

# convert all notebooks to python files into the nbconverted folder
jupyter nbconvert --to python --output-dir=nbconverted/ *.ipynb

# run the python script
python nbconverted/process_and_normalize_jump_data.py
