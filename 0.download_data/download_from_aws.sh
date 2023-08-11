#!/usr/bin/bash
# Bash script called by python script to download the sqlite plate data
#
# Define the CSV file path that specifies the download location
csv_file=$1

# Column name to extract (provide the column name here)
column_name="$3"

# Read the first line of the CSV file to get the column indices
IFS=',' read -r -a header < "$csv_file"
column_index=-1
for idx in "${!header[@]}"; do
    if [[ "${header[$idx]}" == "$column_name" ]]; then
        column_index=$idx
        break
    fi
done

# Check if the column name exists in the header
if [ $column_index -eq -1 ]; then
    echo "Column name not found in the CSV file."
    exit 1
fi

# Read the CSV file line by line (skipping the first line which contains the header)
tail -n +2 "$csv_file" | while IFS=',' read -r -a row; do
    # Get the value of the specific column
    column_value="${row[$column_index]}"

    # Download the s3 file to your local machine in a directory defined by command line argument
    aws s3 cp "$column_value" "$2"
done
