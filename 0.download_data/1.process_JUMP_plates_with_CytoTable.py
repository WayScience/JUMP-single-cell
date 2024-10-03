"""
Processes JUMP plates from manifest using CytoTable
to produce joined compartment data in Parquet format
for use in downstream analysis.
"""

import pathlib
import shutil

import cytotable
import pandas as pd
from parsl.config import Config
from parsl.executors import ThreadPoolExecutor
from pyarrow import parquet

# create plates directory if it doesn't exist already
if not (plates_folder := pathlib.Path("./0.download_data/data/plates")).is_dir():
    plates_folder.mkdir()

# process each plate from the manifest individually
for _, plate_name, plate_s3_path in pd.read_csv(
    "./0.download_data/data/jump_dataset_location_manifest.csv", header=0
).to_records():
    print("Processing plate ", plate_name)

    # create a folder for the plate
    if not (
        plate_folder := pathlib.Path(f"./0.download_data/data/plates/{plate_name}")
    ).is_dir():
        plate_folder.mkdir()

    # if we don't have the cytotable output for a plate, process it
    if not (
        cytotable_output_path := pathlib.Path(
            f"./0.download_data/data/plates/{plate_name}/{plate_name}.parquet"
        )
    ).is_file():
        # process plate using CytoTable
        cytotable_output_path = cytotable.convert(
            source_path=plate_s3_path,
            dest_path=cytotable_output_path,
            dest_datatype="parquet",
            source_datatype="sqlite",
            chunk_size=8000,
            preset="cellprofiler_sqlite_cpg0016_jump",
            # allows AWS S3 requests without login
            no_sign_request=True,
            # use explicit cache to avoid temp cache removal
            local_cache_dir="./0.download_data/jump_sqlite_s3_cache/",
            parsl_config=Config(
                executors=[ThreadPoolExecutor(label="tpe_for_jump_processing")]
            ),
            sort_output=False,
        )

    # read only the metadata from parquet file
    meta = parquet.ParquetFile(cytotable_output_path).metadata
    print(
        "Finished processing plate",
        plate_name,
        "with output",
        cytotable_output_path,
        "which has shape (",
        meta.num_rows,
        ",",
        meta.num_columns,
        ").",
    )

# remove the SQLite plates
shutil.rmtree("./0.download_data/jump_sqlite_s3_cache/")
