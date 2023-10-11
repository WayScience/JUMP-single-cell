# Apply phenotypic profiling model to JUMP data

In this module, we generate single-cell probabilities for each of the 15 phenotypic classes by applying the [phenotypic profiling model](https://github.com/WayScience/phenotypic_profiling_model).
There are two model types, final and shuffled baseline, where single-cell features are randomized independently. 
We output one probability `parquet` file that contains all of the single-cell data per plate and well that contains all relevant metadata.

## Run the prediction notebook

To generate the probabilities for each single cell, run the [evaluate_data.sh](./evaluate_data.sh) file which will convert the notebook into a python file and run it from terminal.

```bash
# Make sure you are in the 2.evaluate_data directory
cd 2.evaluate_data
# Run the notebook as a python script
source evaluate_data.sh
```


