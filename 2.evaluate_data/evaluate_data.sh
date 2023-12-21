#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
eval "$(conda shell.bash hook)"

# activate the main conda environment
conda activate jump_sc

# Directory where the code can be found
target_dir="class_balanced_log_reg_areashape_predict_sc_probabilities"

# run the bash script
"./${target_dir}/process_plates"
