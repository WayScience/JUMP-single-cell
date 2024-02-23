# Analyze Predicted Probabilities

In this module, we perform multiple analyses on the predicted probability data to validate the phenotypic predictions for each treatment (e.g., compound, CRISPR, or ORF).
To compare treatments and the negative control groups, we perform KS tests.

## Analyze Well Probabilities
We compare the phenotype probabilities between each treated well and the remaining negative control wells on the corresponding plate.
Each treatment well and corresponding negative control well phenotype probabilities are only compared if the number of cells in these groups is above a given cell count threshold.
The group, treatment cells or control cells, are then randomly down-sampled depending on which of these groups has a larger population of cells.
Random sampling of the control cells is accomplished through stratification of cells by the plate's wells.
After sampling the cell population, the cells from the treated and control groups are compared using the KS test statistic.

We have found that the predicted probabilities generated from [non-shuffled](https://github.com/WayScience/phenotypic_profiling_model/blob/main/2.train_model/models/multi_class_models/final__CP_areashape_only__balanced.joblib) and [shuffled](https://github.com/WayScience/phenotypic_profiling_model/blob/main/2.train_model/models/multi_class_models/shuffled_baseline__CP__balanced.joblib) weighted logistic regression models seem to perform the best from validation. These models were trained exclusively from [mitocheck](https://github.com/WayScience/mitocheck_data) cellprofiler areashape morphology features.

## Run the analysis notebooks

To perform the analyses, run the [analyze_data.sh](./analyze_data.sh) file which will convert the notebook into a python file and run it from terminal.

```bash
# Make sure you are in the 3.analyze_data directory
cd 3.analyze_data
# Run the notebook as a python script
source analyze_data.sh
```
