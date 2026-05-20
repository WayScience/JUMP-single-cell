# Apply phenotypic profiling models to JUMP data

This module generates single-cell probabilities for 15 phenotypic classes using trained morphology models.
Current workflows focus on class-balanced logistic regression prediction runs and related per-plate processing.

Outputs are written as `parquet` files with phenotypic probabilities and relevant metadata.

## Run predictions

To generate probabilities, run [evaluate_data.sh](./evaluate_data.sh):

```bash
# make sure you are in the 2.evaluate_data directory
cd 2.evaluate_data
# run prediction pipeline
source evaluate_data.sh
```

`evaluate_data.sh` executes the active prediction workflow in `class_balanced_log_reg_areashape_predict_sc_probabilities/`.
