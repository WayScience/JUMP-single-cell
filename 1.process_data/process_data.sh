#!/bin/bash

py_path="nbconverted"

# convert all notebooks to python files into the nbconverted folder
jupyter nbconvert --to python --output-dir="${py_path}/" *.ipynb

python3 "$py_path/normalize_jump_pilot.py"
python3 "$py_path/feature_select_jump_pilot.py"
