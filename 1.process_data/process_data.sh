#!/bin/bash

py_path="nbconverted"

# convert all notebooks to python files into the nbconverted folder
jupyter nbconvert --to python --output-dir="${py_path}/" *.ipynb

# Run all Python files in the folder
for pfile in "$py_path"/*.py; do
    echo "Running $pfile"
    python3 "$pfile"
done
