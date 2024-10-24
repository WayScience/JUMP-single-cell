#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash

# activate the main conda environment
conda activate jump_sc

# convert all notebooks to python files into the nbconverted folder
jupyter nbconvert --to python --output-dir=nbconverted/ *.ipynb

# run the per-treatment analysis
python3 nbconverted/analyze_predicted_probabilities.py

# runt the per-well analysis
python3 nbconverted/log_reg_class_balanced_areashape_analyze_well_predicted_probabilities.py
