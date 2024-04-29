#!/bin/bash

# Get the root directory
git_root=$(git rev-parse --show-toplevel)

py_path="nbconverted"

# convert all notebooks to python files into the nbconverted folder
jupyter nbconvert --to python --output-dir="${py_path}/" *.ipynb

#python3 "$py_path/normalize_jump_pilot.py"

# Get the normalized data path (with multiple plates)
norm_data_path="${git_root}/big_drive/normalized_sc_data"

# Check if the folder exists
if [ -d "$norm_data_path" ]; then

    # Iterate through all Parquet files in the normalized data path
    for file in "$norm_data_path"/*.parquet; do

        start_time=$(date +%s.%N)

        # Check if each path is a file
        if [ -f "$file" ]; then

            # Get the plate name from the filename
            plate_name="$(ls $file | awk -F "/" '{print $NF}' | awk -F "_" '{print $1}')"

            echo ""
            echo "Processing Plate $plate_name"

            # Generate the probabilities for the specified plate data
            python3 "$py_path/feature_select_jump_pilot.py" $file $plate_name

        fi

        end_time=$(date +%s.%N)
        runtime=$(echo "$end_time - $start_time" | bc)
        echo "Plate $plate_name was executed in $runtime seconds"

    done
fi
