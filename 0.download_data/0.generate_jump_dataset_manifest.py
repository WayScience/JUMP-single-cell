r"""°°°
# Creates and stores the aws s3 plate data paths
°°°"""
#|%%--%%| <BjXwKHb2UD|Sj3yqPgfXf>
r"""°°°
## Imports
°°°"""
#|%%--%%| <Sj3yqPgfXf|7CjICyvASe>

import pandas as pd
import pathlib

#|%%--%%| <7CjICyvASe|MWVwTo28Kp>
r"""°°°
## Create the output path if it doesn't exist
°°°"""
#|%%--%%| <MWVwTo28Kp|VvRJxNUbeZ>

output_path = pathlib.Path("data")
output_path.mkdir(parents=True, exist_ok=True)

#|%%--%%| <VvRJxNUbeZ|oxnis1s37X>
r"""°°°
## Store the plate paths
°°°"""
#|%%--%%| <oxnis1s37X|0jG0Szi8qZ>

source = "source_4"
batch = "2020_11_04_CPJUMP1"
data_locations = f"s3://cellpainting-gallery/cpg0000-jump-pilot/{source}/workspace/backend/{batch}"

object_names = ["BR00116991", "BR00116992", "BR00116993", "BR00116994", "BR00116995", "BR00116996", "BR00116997", "BR00116998", "BR00116999", "BR00117000", "BR00117001", "BR00117002", "BR00117003", "BR00117004", "BR00117005", "BR00117006", "BR00117008", "BR00117009", "BR00117010", "BR00117011", "BR00117012", "BR00117013", "BR00117015", "BR00117016", "BR00117017", "BR00117019", "BR00117020", "BR00117021", "BR00117022", "BR00117023", "BR00117024", "BR00117025", "BR00117026", "BR00117050", "BR00117051", "BR00117052", "BR00117053", "BR00117054", "BR00117055", "BR00118039", "BR00118040", "BR00118041", "BR00118042", "BR00118043", "BR00118044", "BR00118045", "BR00118046", "BR00118047", "BR00118048", "BR00118049", "BR00118050"]

sqlite_file = [f"{data_locations}/{obj_name}/{obj_name}.sqlite" for obj_name in object_names]

manifest_df = pd.DataFrame(
        {"plate": object_names,
         "sqlite_file": sqlite_file,
         })

#|%%--%%| <0jG0Szi8qZ|vGbVlO6ord>
r"""°°°
## Save the paths data
°°°"""
#|%%--%%| <vGbVlO6ord|B670chhgfO>

manifest_df.to_csv(output_path / "jump_dataset_location_manifest.csv", index=False)
