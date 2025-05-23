#!/bin/bash
# Aggregates both the normalized and feature-selected single-cell plate data (using the mean) to the well level.

big_drive="$(git rev-parse --show-toplevel)/big_drive"

py_path="nbconverted"

jupyter nbconvert --to python --output-dir="${py_path}/" aggregate_jump_pilot.ipynb

normalized_data_path="${big_drive}/normalized_sc_data"
feature_selected_data_path="${big_drive}/feature_selected_sc_data"

aggregate() {
#   Parameters
#   ----------
#   $1: String
#       Path of the plate data to be aggregated.
#   $2: String
#       Name of the type of data aggregated.

    if [ -d "$1" ]; then
        for file in "$1"/*.parquet; do
            if [ -f "$file" ]; then
                plate_name="$(basename "$file" | awk -F "_" '{print $1}')"

                echo ""
                echo "Processing Plate $plate_name"

                /usr/bin/time -v python3 "$py_path/aggregate_jump_pilot.py" "$file" "$plate_name" "$2"
            fi
        done
    else
        echo "Error: '$1' is not a directory."
        return 1
    fi
}

aggregate "$normalized_data_path" "pre_feature_selection"
aggregate "$feature_selected_data_path" "post_feature_selection"
