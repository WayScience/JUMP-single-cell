#!/bin/bash

# This script calls python code to compute single-cell anomaly data with all datasets.

conda init bash
conda activate jump_sc

# Get the root directory
git_root=$(git rev-parse --show-toplevel)

py_path="nbconverted"

jupyter nbconvert --to python --output-dir="${py_path}/" ./*.ipynb

iso_forest_paths="${git_root}/2.evaluate_data/train_sc_anomalyze_models/isolation_forest_models"
big_drive_path="${1:-/mnt/big_drive}"
anomaly_data_path="${2:-${big_drive_path}/sc_anomaly_data}"


# Get the single-cell data path (with multiple plates)
plate_paths=(
    "${big_drive_path}/feature_selected_sc_qc_data"
    "${big_drive_path}/normalized_sc_qc_data"
    "${big_drive_path}/feature_selected_sc_data"
    "${big_drive_path}/normalized_sc_data"
)

for plate_dir in "${plate_paths[@]}"; do

    if [ -d "$plate_dir" ]; then

        echo -e "\nComputing anomaly data and feature importance data from $plate_dir"
        for file in "$plate_dir"/*.parquet; do

            if [ -f "$file" ]; then

                iso_forest_path="$iso_forest_paths/$(basename "$plate_dir")_isolation_forest.joblib"

                /usr/bin/time -v python3 "$py_path/compute_sc_anomaly_data.py" "$file" "$iso_forest_path" "$anomaly_data_path"

            fi

        done

    else
        echo "Error: '$plate_dir' is not a directory."
        return 1
    fi

done

/usr/bin/time -v python3 "$py_path/compute_sc_feature_importance_data.py" --big_drive_path "$big_drive_path"
/usr/bin/time -v python3 "$py_path/compute_aggregate_treatment_anomaly_data.py" --big_drive_path "$big_drive_path"
