# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: jump_sc (Python)
#     language: python
#     name: jump_sc
# ---

# # coSMicQC Demonstration with JUMP Plate BR00117006

# +
import json
import pathlib

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from cloudpathlib import S3Client

# +
# reference the file without reading it entirely
target_file = pq.ParquetFile("data/plates/BR00117006/BR00117006.parquet")

# target image names
target_image_names = [
    "CellOutlines",
    "NucleiOutlines",
    "OrigAGP",
    "OrigDNA",
    "OrigRNA",
]

# create a column grouping for the columns we're interested in
target_image_column_groups = [
    (f"Image_PathName_{name}", f"Image_FileName_{name}") for name in target_image_names
]
# flatten the groupings from above
target_flattened_columns = [
    # flatten the groupings from above
    col
    for colgroup in target_image_columns
    for col in colgroup
]

# show the paired column names
print(json.dumps(target_image_column_groups, indent=4))

# check that the columns where images are included
print(
    json.dumps(
        [
            col
            for col in target_file.schema.names
            if any(target in col for target in target_flattened_columns)
        ],
        indent=4,
    )
)

# +
# show first row of output to help determine where files are located
# note: we do this to avoid reading the full dataset, which is > 20 GB
df_example = pa.Table.from_batches(
    [next(target_file.iter_batches(batch_size=1))]
).to_pandas()[target_flattened_columns]

# print the dictionary with indentation from the json module
print(json.dumps(df_example.to_dict(orient="records"), indent=4))

# +
# create inferred AWS S3 paths for all images using the example
s3_columns = []

for pathname_col, filename_col in target_image_column_groups:

    # form a column name for the s3 path
    s3_column_name = f"Image_S3Path_{filename_col.replace('Image_FileName_', '')}"

    # form an S3 path for the outlines, which are stored separately from originals
    if "Outlines" in filename_col:
        df_example[s3_column_name] = (
            df_example[pathname_col].str.replace(
                "/home/ubuntu/local_output/",
                "s3://cellpainting-gallery/cpg0000-jump-pilot/source_4/workspace/analysis/2020_11_04_CPJUMP1/",
            )
            + "/"
            + df_example[filename_col]
        )

    # form an S3 path for the originals
    if "Orig" in filename_col:
        df_example[s3_column_name] = (
            df_example[pathname_col].str.replace(
                "/home/ubuntu/local_input/projects/2019_07_11_JUMP-CP/2020_11_04_CPJUMP1/",
                "s3://cellpainting-gallery/cpg0000-jump-pilot/source_4/images/2020_11_04_CPJUMP1/",
            )
            + "/"
            + df_example[filename_col]
        )

    # collect the s3 column name
    s3_columns.append(s3_column_name)

# print the dictionary with indentation from the json module
print(json.dumps(df_example.to_dict(orient="records"), indent=4))

# +
# create a custom s3 client to utilize no-sign-request (for anonymous access to s3 resources)
s3_cli = S3Client(no_sign_request=True)

# create paths
pathlib.Path("data/images/outlines").mkdir(exist_ok=True, parents=True)
pathlib.Path("data/images/orig").mkdir(exist_ok=True, parents=True)

# download images
for record in df_example[s3_columns].to_dict(orient="records"):

    # iterate through all s3 columns
    for s3_column in s3_columns:

        # create a cloudpath
        image_cloudpath = s3_cli.CloudPath(record[s3_column])

        # download outlines images
        if "Outlines" in s3_column:
            image_cloudpath.download_to(f"data/images/outlines/{image_cloudpath.name}")

        # download outlines images
        if "Orig" in s3_column:
            image_cloudpath.download_to(f"data/images/orig/{image_cloudpath.name}")
# -

# show the data tree
# !tree data


