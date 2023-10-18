# Analyze predicted probability output

In this module, we perform multiple analyses on the predicted probability data to validate the phenotypic predictions for each treatment (e.g., compound, CRISPR, or ORF).
To compare treatment and the negative control groups, we perform post-hoc statistical analyses such as:

1. Mann-whitney U test
2. T-test
3. Dunn test 

These tests compute the median to determine the directionality of significance among treatments compared to control.

## Run the analysis notebooks

To perform the analyses, run the [analyze_data.sh](./analyze_data.sh) file which will convert the notebook into a python file and run it from terminal.

```bash
# Make sure you are in the 3.analyze_data directory
cd 3.analyze_data
# Run the notebook as a python script
source analyze_data.sh
```
