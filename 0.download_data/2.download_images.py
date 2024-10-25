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

# # 2.Download JUMP Plate BR00117006 Images and Outlines
#
# This notebook works towards demonstrating how to download JUMP Plate BR00117006 images and outlines.

# +
import json
import pathlib
from typing import List, Tuple

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from cloudpathlib import S3Client


# +
def download_jump_cpg000_images_from_s3(
    df: pd.DataFrame,
    s3_columns: List[str],
    data_path: str,
) -> str:
    """
    Downloads images from S3 paths in specified
    columns of the DataFrame.

    Creates local directories if they do not exist
    and downloads files from S3 paths listed
    in the specified columns, using anonymous
    (no-sign-request) access.

    Args:
        df (pd.DataFrame):
            The DataFrame containing columns
            with S3 paths.
        s3_columns (List[str]):
            List of column names in `df`
            that contain the S3 paths.
        data_path (str):
            A path where images will be downloaded.

    Returns:
        str:
            string based path to the images dir
    """

    # create a custom s3 client to utilize no-sign-request
    # (for anonymous access to s3 resources)
    s3_client = S3Client(no_sign_request=True)

    # Create directories for downloading images
    pathlib.Path(f"{data_path}/outlines").mkdir(parents=True, exist_ok=True)
    pathlib.Path(f"{data_path}/orig").mkdir(parents=True, exist_ok=True)

    # Iterate over each record in the DataFrame and download the images
    for record in df[s3_columns].to_dict(orient="records"):
        for s3_column in s3_columns:
            image_cloudpath = s3_client.CloudPath(record[s3_column])

            # Download outlines images
            if "Outlines" in s3_column:
                image_cloudpath.download_to(
                    f"data/images/outlines/{image_cloudpath.name}"
                )

            # Download original images
            elif "Orig" in s3_column:
                image_cloudpath.download_to(f"data/images/orig/{image_cloudpath.name}")

    return "data/images"


def add_jump_cpg0000_s3_paths(
    df: pd.DataFrame, image_column_groups: List[Tuple[str, str]]
) -> pd.DataFrame:
    """
    Add inferred AWS S3 paths to the DataFrame based
    on given image path and file name columns.

    For each pair of columns in `image_column_groups`,
    this function creates a new S3 path column
    in the DataFrame. The new columns contain S3
    paths for either "Outlines" or "Orig" files,
    depending on the filename column contents.

    Args:
        df (pd.DataFrame):
            The DataFrame containing the local path
            and filename columns.
        image_column_groups (List[Tuple[str, str]]):
            A list of tuples, where each tuple
            contains two strings: the pathname
            column name and the filename column name.

    Returns:
        pd.DataFrame, List[str]:
            The original DataFrame with additional
            columns for the inferred S3 paths and a
            list which includes the s3 column name strings.

    """
    s3_columns = []

    for pathname_col, filename_col in image_column_groups:
        # Define the new S3 column name
        s3_column_name = f"Image_S3Path_{filename_col.replace('Image_FileName_', '')}"

        # Generate the S3 path for outline images
        if "Outlines" in filename_col:
            df[s3_column_name] = (
                df[pathname_col].str.replace(
                    "/home/ubuntu/local_output/",
                    (
                        "s3://cellpainting-gallery/cpg0000-jump-pilot/source_4/"
                        "workspace/analysis/2020_11_04_CPJUMP1/"
                    ),
                    regex=False,
                )
                + "/"
                + df[filename_col]
            )

        # Generate the S3 path for original images
        elif "Orig" in filename_col:
            df[s3_column_name] = (
                df[pathname_col].str.replace(
                    "/home/ubuntu/local_input/projects/2019_07_11_JUMP-CP/2020_11_04_CPJUMP1/",
                    (
                        "s3://cellpainting-gallery/cpg0000-jump-pilot/source_4/"
                        "images/2020_11_04_CPJUMP1/"
                    ),
                    regex=False,
                )
                + "/"
                + df[filename_col]
            )

        # Collect the new S3 column name
        s3_columns.append(s3_column_name)

    return df, s3_columns


# +
# reference the file without reading it entirely
target_file = pq.ParquetFile(
    "../0.download_data/data/plates/BR00117006/BR00117006.parquet"
)

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
    for colgroup in target_image_column_groups
    for col in colgroup
]

# show the paired column names
print(json.dumps(target_image_column_groups, indent=4))

# check that the columns where images are included
print(
    json.dumps(
        [col for col in target_file.schema.names if col in target_flattened_columns],
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
df_example, s3_columns = add_jump_cpg0000_s3_paths(
    df=df_example, image_column_groups=target_image_column_groups
)

# print the dictionary with indentation from the json module
print(json.dumps(df_example.to_dict(orient="records"), indent=4))
# -

# download the images to a local path
image_path = download_jump_cpg000_images_from_s3(
    df=df_example, s3_columns=s3_columns, data_path="data/images"
)
image_path

# show the images
print(
    "Outlines:",
    json.dumps(
        [
            str(path)
            for path in list(pathlib.Path(image_path).rglob("*.png"))
            if ".ipynb_checkpoints/" not in str(path)
        ],
        indent=4,
    ),
)
print(
    "Originals:",
    json.dumps(
        [
            str(path)
            for path in list(pathlib.Path(image_path).rglob("*.tiff"))
            if ".ipynb_checkpoints/" not in str(path)
        ],
        indent=4,
    ),
)
