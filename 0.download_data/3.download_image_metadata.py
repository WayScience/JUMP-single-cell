# %% [markdown]
# # Download and Save Image Metadata
# %%

from pathlib import Path, PurePosixPath

import pandas as pd
import s3fs

# %% [markdown]
# ## Paths and Names
# %%

bucket = "cellpainting-gallery"
run_name = "2020_11_04_CPJUMP1"
prefix = f"cpg0000-jump-pilot/source_4/workspace/load_data_csv/{run_name}"

output_path = Path(f"image_metadata/{run_name}_all_plates.parquet")

s3_glob = f"{bucket}/{prefix}/*/load_data.csv"

# %% [markdown]
# ## Download and Concatenate Metadata
# %%
storage_options = {"anon": True}

fs = s3fs.S3FileSystem(anon=True)
csv_keys = sorted(fs.glob(s3_glob))

if not csv_keys:
    raise FileNotFoundError(f"No files found for pattern: s3://{s3_glob}")

print(f"Found {len(csv_keys)} plate CSV files under {run_name}")

meta_img_df = []
for key in csv_keys:
    s3_url = f"s3://{key}"
    plate = PurePosixPath(key).parts[-2]

    print(f"Reading: {s3_url}")
    meta_plate_img_df = pd.read_csv(s3_url, storage_options=storage_options)
    meta_plate_img_df["source_plate"] = plate
    meta_plate_img_df["source_s3_path"] = s3_url
    meta_img_df.append(meta_plate_img_df)

meta_img_df = pd.concat(meta_img_df, axis=0, ignore_index=True)

# %%
col_mask = meta_img_df.columns.str.contains("URL")
url_cols = meta_img_df.columns[col_mask].tolist()

id_cols = meta_img_df.columns[~col_mask].tolist()

meta_img_df = meta_img_df.melt(
    id_vars=id_cols,
    value_vars=url_cols,
    var_name="Metadata_ChannelURLName",
    value_name="Metadata_FileUrl",
)

# %% [markdown]
# ## Save Metadata
# %%
output_path.parent.mkdir(parents=True, exist_ok=True)
meta_img_df.to_parquet(output_path, index=False)

print(f"Saved merged Parquet to: {output_path}")
print(f"Merged shape: {meta_img_df.shape}")
