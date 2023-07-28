r"""°°°
# Download sqlite plate data from aws
Note, this script was not rerun to display the outputs for the sake of time. To download the data, you must be signed into your aws account
°°°"""
#|%%--%%| <7T0gePh3Zn|ddhh5egm7R>
r"""°°°
## Imports
°°°"""
# |%%--%%| <ddhh5egm7R|XqllLfeEBZ>

import pathlib
import subprocess

# |%%--%%| <XqllLfeEBZ|q52bES5PJV>
r"""°°°
## Find the root of the git directory
This allows file paths to be referenced in a system agnostic way
°°°"""
# |%%--%%| <q52bES5PJV|xCbL8BuHjD>

# Get the current working directory
cwd = pathlib.Path.cwd()

if (cwd / ".git").is_dir():
    root_dir = cwd

else:
    root_dir = None
    for parent in cwd.parents:
        if (parent / ".git").is_dir():
            root_dir = parent
            break

# Check if a Git root directory was found
if root_dir is None:
    raise FileNotFoundError("No Git root directory found.")

# |%%--%%| <xCbL8BuHjD|DgPm3tAEsr>
r"""°°°
## Download the plate sqlite data from AWS S3
°°°"""
# |%%--%%| <DgPm3tAEsr|NDX1gPfGsN>

# Specify the data path for downloading the data
download_map = "jump_paths.csv"

# Specify the location to save the data
save_location = f"{root_dir}/big_drive/data"

# Create the necessary directories if non-existent
pathlib.Path(save_location).mkdir(parents=True, exist_ok=True)

# Download the data using a bash script
subprocess.run(["bash", "download_from_aws.sh", download_map, save_location])
