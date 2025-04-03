#!/bin/bash

# This script calls python code to sample and train anomalyze by passing plates from processed data as input.

sampled_plate_jump_data=$(mktemp -d)

# Get the root directory
git_root=$(git rev-parse --show-toplevel)

py_path="nbconverted"

jupyter nbconvert --to python --output-dir="${py_path}/" *.ipynb

# Get the normalized data path (with multiple plates)
plate_paths=(
    "${git_root}/big_drive/feature_selected_sc_qc_data"
    "${git_root}/big_drive/normalized_sc_qc_data"
    "${git_root}/big_drive/feature_selected_sc_data"
    "${git_root}/big_drive/normalized_sc_data"
    "${git_root}/big_drive/post_feature_selection_aggregated_data_pre_qc"
    "${git_root}/big_drive/pre_feature_selection_aggregated_data_pre_qc"
    "${git_root}/big_drive/post_feature_selection_aggregated_data_qc"
    "${git_root}/big_drive/pre_feature_selection_aggregated_data_qc"
)

for plate_dir in "${plate_paths[@]}"; do

    if [ -d "$plate_dir" ]; then

        if [[ "$plate_dir" == *"sc"* ]]; then
            is_sc="true"
        else
            is_sc="false"
        fi

        echo -e "\nSampling from $plate_dir"

        for plate_file in $plate_dir/*; do
            /usr/bin/time -v python3 "$py_path/sample_anomalous_single_cells_fs.py" "$plate_file" "$is_sc" "$sampled_plate_jump_data"
        done

        echo -e "\nTraining on sampled data from $plate_dir"

        /usr/bin/time -v python3 "$py_path/identify_anomalous_single_cells_fs.py" "$plate_dir" "$is_sc" "$sampled_plate_jump_data"

    else
        echo "Error: '$plate_dir' is not a directory."
        return 1
    fi

done
