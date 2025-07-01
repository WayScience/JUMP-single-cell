#!/bin/bash

set -euo pipefail

ANOMALY_DATASET_PATH="$1"
PLATE_NAME="$2"
MORPHOLOGY_DATASET_PATH="$3"
MODEL_PATH="$4"
FEATURE_IMPORTANCE_OUTPUT_PATH="$5"
PLATE_MAPPING_PATH="$6"
PYTHON_SCRIPT="$7"

python3 "$PYTHON_SCRIPT" \
    --anomaly_dataset_path "$ANOMALY_DATASET_PATH" \
    --plate "$PLATE_NAME" \
    --morphology_dataset_path "$MORPHOLOGY_DATASET_PATH" \
    --model_path "$MODEL_PATH" \
    --feature_importances_output_path "$FEATURE_IMPORTANCE_OUTPUT_PATH" \
    --plate_mapping_path "$PLATE_MAPPING_PATH"
