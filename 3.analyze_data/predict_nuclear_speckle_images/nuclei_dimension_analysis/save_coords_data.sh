#!/bin/bash

CSV_FILE="../../../reference_plate_data/barcode_platemap.csv"
METADATA_PATHS="../jump_data/profiles/plates"

if [[ ! -f "$CSV_FILE" ]]; then
    echo "CSV file not found!"
    exit 1
fi

while IFS=',' read -r plate_name platemap_type; do
    if [[ "$platemap_type" == *"compound"* ]]; then
        echo "Platename: $plate_name"
        echo "Platemap Type: $platemap_type"
        python3 save_coords_plate.py "$METADATA_PATHS/$plate_name/$plate_name.parquet"
    fi
done < "$CSV_FILE"
