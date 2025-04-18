#!/bin/bash

# This script calls python code to compute single-cell anomaly data with all datasets.

conda init bash
conda activate jump_sc

# Get the root directory
git_root=$(git rev-parse --show-toplevel)

py_path="nbconverted"

jupyter nbconvert --to python --output-dir="${py_path}/" ./*.ipynb

iso_forest_paths=f"${git_root}/2.evaluate_data/train_sc_anomalyze_models/isolation_forest_models"

# Get the normalized data path (with multiple plates)
plate_paths=(
    "${git_root}/big_drive/feature_selected_sc_qc_data"
    "${git_root}/big_drive/normalized_sc_qc_data"
    "${git_root}/big_drive/feature_selected_sc_data"
    "${git_root}/big_drive/normalized_sc_data"
)

for plate_dir in "${plate_paths[@]}"; do

    if [ -d "$plate_dir" ]; then

        iso_forest_path="$iso_forest_paths/$(basename "$plate_dir")_isolation_forest.joblib"

        echo -e "\nSampling from $plate_dir"

        /usr/bin/time -v python3 "$py_path/compute_sc_outlier_data.py" "$plate_dir" "$iso_forest_path"

    else
        echo "Error: '$plate_dir' is not a directory."
        return 1
    fi

done
