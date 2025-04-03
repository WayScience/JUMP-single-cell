#!/bin/bash

# This script calls python code to identify anomalous cells by passing each plate as input.

# Record the start time of the script
script_start_time=$(date +%s.%N)

# Get the root directory
git_root=$(git rev-parse --show-toplevel)

py_path="nbconverted"

# convert all notebooks to python files into the nbconverted folder
jupyter nbconvert --to python --output-dir="${py_path}/" *.ipynb

# Get the normalized data path (with multiple plates)
feature_selected_data_path="${git_root}/big_drive/feature_selected_sc_data"

# Track the number of plates processed
number_plates=0

# Check if the folder exists
if [ -d "$feature_selected_data_path" ]; then

    # Iterate through all Parquet files in the normalized data path
    for file in "$feature_selected_data_path"/*.parquet; do

        start_time=$(date +%s.%N)

        # Check if each path is a file
        if [ -f "$file" ]; then

            # Get the plate name from the filename
            plate_name="$(ls $file | awk -F "/" '{print $NF}' | awk -F "_" '{print $1}')"

            echo -e "\nProcessing Plate $plate_name"

            # Generate the probabilities for the specified plate data
            python3 "$py_path/identify_anomalous_single_cells_fs.py" $file $plate_name

            ((number_plates++))

        fi

        end_time=$(date +%s.%N)
        runtime=$(echo "($end_time - $start_time) / 3600" | bc)
        echo "Plate $plate_name was executed in $runtime hours"

    done
fi

script_end_time=$(date +%s.%N)

# Show execution summary
script_runtime=$(echo "($script_end_time - $script_start_time) / 3600" | bc)
echo -e "\nScript processed $number_plates plates in $script_runtime hours"
