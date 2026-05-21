# Analyze Predicted Probabilities

In this module, we perform analyses on predicted probability data to evaluate phenotypic behavior across treatments (for example, compound, CRISPR, and ORF).
Core comparisons use KS-based testing against negative control groups.

## Analyze Well Probabilities
We compare the phenotype probabilities between each treated well and the remaining negative control wells on the corresponding plate.
Each treatment well and corresponding negative control well phenotype probabilities are only compared if the number of cells in these groups is above a given cell count threshold.
The group, treatment cells or control cells, are then randomly down-sampled depending on which of these groups has a larger population of cells.
Random sampling of control cells is done through stratification by plate and well.
After sampling the cell population, the cells from the treated and control groups are compared using the KS test statistic.

The analysis scripts in this directory include well-level aggregation within plates (summarizing single-cell probabilities per well), treatment-level aggregation across wells, significance testing, and probability distribution visualization.

## Run the Analysis Notebooks

To perform the analyses, run [analyze_data.sh](./analyze_data.sh).

```bash
# make sure you are in the 3.analyze_data directory
cd 3.analyze_data
# run analysis workflow
source analyze_data.sh
```
