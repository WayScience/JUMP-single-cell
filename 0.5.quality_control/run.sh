#!/bin/bash
# Runs processing related to step 5.quality_control
set -e

# run umap analysis via python script based on notebook
# use a subshell to keep existing code intact
(
cd ./0.quality_control || exit
conda run -n jump_sc python ./0.jump_umap_analysis_with_cosmicqc.py
)
