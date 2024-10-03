#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash

# convert all notebooks to python files into the nbconverted folder
conda run -n jump_sc jupyter nbconvert --to python \
    --output-dir=nbconverted/ \
    *.ipynb

# download the jump manifest data
conda run -n jump_sc python nbconverted/0.generate_jump_dataset_manifest.py

# process the plate data using cytotable
conda run -n jump_sc python 1.process_JUMP_plates_with_CytoTable.py
