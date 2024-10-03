"""
Processes JUMP plates from manifest using CytoTable
to produce joined compartment data in Parquet format
for use in downstream analysis.
"""

import cytotable
import pathlib
import pandas as pd

if not (plates_folder := pathlib.Path(f"./data/plates")).is_dir():
    plates_folder.mkdir()

for _, plate_name, plate_s3_path in pd.read_csv(
    "data/jump_dataset_location_manifest.csv", header=0
).to_records():

    print("Processing plate ", plate_name)
    if not (plate_folder := pathlib.Path(f"./data/plates/{plate_name}")).is_dir():
        plate_folder.mkdir()

    break
