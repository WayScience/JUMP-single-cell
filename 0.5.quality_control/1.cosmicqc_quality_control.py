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

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# show the columns where images are included
[
    col
    for col in pq.ParquetFile("data/plates/BR00117006/BR00117006.parquet").schema.names
    if any(word in col for word in ["Path", "File"])
]


