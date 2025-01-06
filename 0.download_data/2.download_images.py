# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.6
#   kernelspec:
#     display_name: jump_sc (Python)
#     language: python
#     name: jump_sc
# ---

# + [markdown] papermill={"duration": 0.004479, "end_time": "2025-01-06T22:28:25.422676", "exception": false, "start_time": "2025-01-06T22:28:25.418197", "status": "completed"}
# # 2.Download JUMP Plate Images and Outlines
#
# This notebook works downloads JUMP plate images 
# and outlines using 
# [Papermill](https://github.com/nteract/papermill) 
# paramterization.

# + editable=true papermill={"duration": 0.008132, "end_time": "2025-01-06T22:28:25.436456", "exception": false, "start_time": "2025-01-06T22:28:25.428324", "status": "completed"} slideshow={"slide_type": ""} tags=["parameters"]
# Papermill notebook parameters
# (including notebook cell tag).
# We set a default here which may be overridden
# during Papermill execution.
# See here for more information:
# https://papermill.readthedocs.io/en/latest/usage-parameterize.html
plate_id = "BR00117006"

# + editable=true papermill={"duration": 3.150857, "end_time": "2025-01-06T22:28:28.598904", "exception": false, "start_time": "2025-01-06T22:28:25.448047", "status": "completed"} slideshow={"slide_type": ""}
import json
import pathlib
from typing import List, Tuple

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from cloudpathlib import S3Client


# + papermill={"duration": 0.021248, "end_time": "2025-01-06T22:28:28.623359", "exception": false, "start_time": "2025-01-06T22:28:28.602111", "status": "completed"}
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
    pathlib.Path(base_outline_path := f"{data_path}/outlines").mkdir(
        parents=True, exist_ok=True
    )
    pathlib.Path(base_orig_path := f"{data_path}/orig").mkdir(
        parents=True, exist_ok=True
    )

    # Iterate over each record in the DataFrame and download the images
    for record in df[s3_columns].to_dict(orient="records"):
        for s3_column in s3_columns:
            image_cloudpath = s3_client.CloudPath(record[s3_column])

            # Download outlines images
            if "Outlines" in s3_column:
                candidate_path = f"{base_outline_path}/{image_cloudpath.name}"
                if not pathlib.Path(candidate_path).is_file():
                    image_cloudpath.download_to(candidate_path)

            # Download original images
            elif "Orig" in s3_column:
                candidate_path = f"{base_orig_path}/{image_cloudpath.name}"
                if not pathlib.Path(candidate_path).is_file():
                    image_cloudpath.download_to(candidate_path)

    return "data/images"


# + editable=true papermill={"duration": 0.20375, "end_time": "2025-01-06T22:28:28.832306", "exception": false, "start_time": "2025-01-06T22:28:28.628556", "status": "completed"} slideshow={"slide_type": ""}
# reference the file without reading it entirely
target_file = pq.ParquetFile(
    (parquet_path := f"../0.download_data/data/plates/{plate_id}/{plate_id}.parquet")
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

# + editable=true papermill={"duration": 0.410698, "end_time": "2025-01-06T22:28:29.244472", "exception": false, "start_time": "2025-01-06T22:28:28.833774", "status": "completed"} slideshow={"slide_type": ""}
# show first row of output to help determine where files are located
# note: we do this to avoid reading the full dataset, which is > 20 GB
df_example = pa.Table.from_batches(
    [next(target_file.iter_batches(batch_size=1))]
).to_pandas()[target_flattened_columns]

# print the dictionary with indentation from the json module
print(json.dumps(df_example.to_dict(orient="records"), indent=4))

# + papermill={"duration": 0.007916, "end_time": "2025-01-06T22:28:29.253908", "exception": false, "start_time": "2025-01-06T22:28:29.245992", "status": "completed"}
df_example, s3_columns = add_jump_cpg0000_s3_paths(
    df=df_example, image_column_groups=target_image_column_groups
)

# print the dictionary with indentation from the json module
print(json.dumps(df_example.to_dict(orient="records"), indent=4))

# + papermill={"duration": 0.18372, "end_time": "2025-01-06T22:28:29.440437", "exception": false, "start_time": "2025-01-06T22:28:29.256717", "status": "completed"}
# download the images to a local path
image_path = download_jump_cpg000_images_from_s3(
    df=df_example, s3_columns=s3_columns, data_path=f"data/images/{plate_id}"
)
image_path

# + papermill={"duration": 0.107778, "end_time": "2025-01-06T22:28:29.549758", "exception": false, "start_time": "2025-01-06T22:28:29.441980", "status": "completed"}
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

# + editable=true papermill={"duration": 0.508443, "end_time": "2025-01-06T22:28:30.066200", "exception": false, "start_time": "2025-01-06T22:28:29.557757", "status": "completed"} slideshow={"slide_type": ""}
# read the full data
df_full = pd.read_parquet(parquet_path, columns=target_flattened_columns)
df_full

# + papermill={"duration": 0.703436, "end_time": "2025-01-06T22:28:30.776504", "exception": false, "start_time": "2025-01-06T22:28:30.073068", "status": "completed"}
# find the s3 paths for the full dataset
df_full, s3_columns = add_jump_cpg0000_s3_paths(
    df=df_full, image_column_groups=target_image_column_groups
)
df_full

# + editable=true papermill={"duration": 29.614086, "end_time": "2025-01-06T22:29:00.397392", "exception": false, "start_time": "2025-01-06T22:28:30.783306", "status": "completed"} slideshow={"slide_type": ""}
# download the images for the dataset
image_path = download_jump_cpg000_images_from_s3(
    df=df_full, s3_columns=s3_columns, data_path=f"data/images/{plate_id}"
)
