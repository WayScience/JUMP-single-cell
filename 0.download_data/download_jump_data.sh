#!/usr/bin/bash
# Bash script called by python script to download the sqlite plate data
#
# Define the CSV file path that specifies the download location
csv_file=$1

# Column number (starting from 1)
column_number=3

# Read the CSV file line by line
while IFS=',' read -r -a row; do
    # Get the value of the specific column
    column_value="${row[$((column_number))]}"

    # Process the column value (replace with your own logic)
    aws s3 cp $column_value "$2"
done < "$csv_file"
