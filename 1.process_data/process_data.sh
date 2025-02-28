#!/bin/bash
# Merge, Normalize and Feature Select morphology data per plate

git_root=$(git rev-parse --show-toplevel)

py_path="nbconverted"

jupyter nbconvert --to python --output-dir="${py_path}/" *.ipynb

/usr/bin/time -v python3 "$py_path/normalize_jump_pilot.py"

norm_data_path="${git_root}/big_drive/normalized_sc_data"

if [ -d "$norm_data_path" ]; then

    for file in "$norm_data_path"/*.parquet; do

        start_time=$(date +%s.%N)

        if [ -f "$file" ]; then

            plate_name="$(ls $file | awk -F "/" '{print $NF}' | awk -F "_" '{print $1}')"

            echo ""
            echo "Processing Plate $plate_name"

            /usr/bin/time -v python3 "$py_path/feature_select_jump_pilot.py" $file $plate_name

         else
            echo "Error: '$1' is not a directory."
            return 1
        fi
    done
fi
