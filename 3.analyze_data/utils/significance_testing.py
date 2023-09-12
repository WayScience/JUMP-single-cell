import pandas as pd
from collections import defaultdict

def store_comparisons(_comp_functions, _treatments, _dmso_probs, _treatment_probs, **_comp_names):
    """
    Parameters
    ----------
    _comp_functions: Dictionary of Dictionaries
        The keys are the names of the statistical tests.
        The keys of the subdictionaries are the following strings {statistical_test_function, comparison_metric}.

    _treatments: Dictionary of Lists
        The treatment results, which contains keys corresponding to the statistical test, the comparison metric, the p value, and the comparison metric value among other keys specified by comp_names.

    _dmso_probs: Pandas Series
        The down-sampled predicted probilities of DMSO for a treatment type and phenotype.
    _treatment_probs: Pandas Series
        The predicted probabilities of the treatment

    **_comp_names: Keywork arguments
        Additional treatment data to include in the results as specified in _treatments

    Returns
    -------
    _treatments: Dictionary of Lists
        The treatment results, which contains keys corresponding to the statistical test, the comparison metric, the p value, and the comparison metric value among other keys specified by comp_names.
    """
    for func_name, func_data in _comp_functions.items():

        # Compute the results of the function use prespeficied parameters
        results = func_data["statistical_test_function"](_dmso_probs, _treatment_probs)

        _treatments["statistical_test"].append(func_name)
        _treatments["comparison_metric"].append(func_data["comparison_metric"])

        # Store subset of results as predetermined
        for name, val in results:
            _treatments[name].append(val)

        # Store the other data associated with the results
        for name, val in _comp_names.items():
            _treatments[name].append(val)

    return _treatments

def filter_wells_by_cell_count(_df, _cutoff):
    """
    Parameters
    ----------
    _df: pandas Dataframe
        The dataframe which contains the well, which will be potentially removed

    _cutoff: Integer
        The number of cells a well must have to remain in the dataframe

    Returns
    -------
    _df: pandas dataframe
        The filtered dataframe with only wells that have more cells than the cutoff
    """

    # Find the number of cells in each well
    well_counts = _df["Metadata_Well"].value_counts()

    # Find the wells that contain more cells than the cutoff
    wells_kept = well_counts[well_counts > _cutoff].index

    # Keep only the cells that contain more cells than the cutoff
    _df = _df.loc[_df["Metadata_Well"].isin(wells_kept)]

    return _df


def get_treatment_comparison(_comp_functions, _treatment_paths, _probadf, _barcode_platemapdf, _control_cutoff = 50, _treat_cutoff = 50):
    """
    Parameters
    ----------
    _comp_functions: Dictionary of Dictionaries
        The keys are the names of the statistical tests.
        The keys of the subdictionaries are the following strings {statistical_test_function, comparison_metric}.
        The statistical_test_function key contains a function as a value, which outputs a zipped result of the statistical test, which must be defined prior to execution.
        The comparison_metric key contains the name of the comparison metric computed as a string

    _treatment_paths: Dictionary of Dictionaries
        The keys of this dictionary are strings of the treatment types {compound, crispr, orf}.
        The dictionaries corresponding to each of these keys have the keys {metadata, platemap, treatment_column, Plate_Map_Name}.
        The metadata dataframe can be accessed with the metadata key, the platemap dataframe can be accessed with the platemap key, and the name of the treatment column can be accessed with the treatment_column key.

    _probadf: pandas Dataframe
        The predicted probabilities and associated metadata for each cell

    _barcode_platemapdf: pandas Dataframe
        Maps the plate to the treatment type

    _control_cutoff: Integer
        The minimum number of cells required for a negative control well to be included in the comparison

    _treat_cutoff: Integer
        The minimum number of cells required for a treatment well (excluding negative control wells) to be included in the comparison

    Returns
    -------
    treatments: Dictionary
        Contains the analysis information corresponding to each treatment
    """

    treatments = defaultdict(list)

    # Store the phenotype columns
    phenotype_cols = [col for col in _probadf.columns if "Metadata" not in col]

    # Columns names to drop after merging data
    drop_cols = ["Assay_Plate_Barcode", "well_position"]

    # Iterate through the treatment data for each treatment type
    for treat_type_name, treat_data in _treatment_paths.items():

        # Get the data corresponding to the current treatment type
        treat_type_platemap = _barcode_platemapdf.loc[_barcode_platemapdf["Plate_Map_Name"] == treat_data["Plate_Map_Name"]]

        # Retrieve the data that correspond to the plate names, where the plate names correspond to the treatment type
        filtered_probadf = pd.merge(_probadf, treat_type_platemap, how="inner", left_on="Metadata_plate", right_on="Assay_Plate_Barcode")

        # Find the treatments that correspond to each well using the broad_sample
        common_broaddf = pd.merge(treat_data["metadata"], treat_data["platemap"], how="inner", on="broad_sample")

        # Combine the probability and treatment data using the well
        common_broaddf = pd.merge(filtered_probadf, common_broaddf, how="inner", left_on="Metadata_Well", right_on="well_position")

        # Drop redundant columns for the merge operations
        common_broaddf.drop(columns=drop_cols, inplace=True)

        # Specify the types of negative controls
        negcondf = common_broaddf.loc[common_broaddf["control_type"] == "negcon"]
        no_negcondf = common_broaddf.loc[common_broaddf["control_type"] != "negcon"]

        # Create comparison groups
        iter_group = set(zip(no_negcondf["Metadata_plate"], no_negcondf["Metadata_model_type"], no_negcondf[treat_data["treatment_column"]]))

        # Iterate through each group
        for plate, model_type, utreat in iter_group:

            # Specify the treatment and negative control dataframes
            treatdf = no_negcondf.loc[(no_negcondf["Metadata_plate"] == plate) & (no_negcondf["Metadata_model_type"] == model_type) & (no_negcondf[treat_data["treatment_column"]] == utreat)]
            negdf = negcondf.loc[(negcondf["Metadata_plate"] == plate) & (negcondf["Metadata_model_type"] == model_type)]

            # Remove wells if the cell count is below the corresponding threshold
            treatdf = filter_wells_by_cell_count(treatdf, _treat_cutoff)
            negdf = filter_wells_by_cell_count(negdf, _control_cutoff)

            # Compute the number of cells for each group
            treat_cell_count = len(treatdf)
            negcon_cell_count = len(negdf)
            min_cell_count = min(treat_cell_count, negcon_cell_count)

            # If there are no probability values that match the given well for some reason analyze the next treatment
            if (min_cell_count > 0):

                # Sample the treatment dataframe if the cell count for the treatments is larger than for the controls
                if treat_cell_count > negcon_cell_count:
                    samp_treat = treatdf.sample(n=min_cell_count, random_state=0)
                    samp_neg = negdf

                # Otherwise, sample the negative control
                else:
                    samp_neg = negdf.sample(n=min_cell_count, random_state=0)
                    samp_treat = treatdf

                # Iterate through each possible phenotype and update the treatments variable
                for pheno in phenotype_cols:

                    treatments = store_comparisons(_comp_functions, treatments, samp_neg[pheno], samp_treat[pheno], phenotype=pheno, treatment_type=treat_type_name, treatment=utreat, model_type=model_type, cell_count=min_cell_count)

    return treatments

