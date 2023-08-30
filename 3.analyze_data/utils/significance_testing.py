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

def get_treatment_comparison(_comp_functions, _treatment_paths, _probadf, _barcode_platemapdf):
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
        The dictionaries corresponding to each of these keys have the keys {metadata, platemap, treatment_column}.
        The metadata dataframe can be accessed with the metadata key, the platemap dataframe can be accessed with the platemap key, and the name of the treatment column can be accessed with the treatment_column key.

    _probadf: pandas Dataframe
        The predicted probabilities and associated metadata for each cell

    _barcode_platemapdf: pandas Dataframe
        Maps the plate to the treatment type

    Returns
    -------
    treatments: Dictionary
        Contains the analysis information corresponding to each treatment
    """

    treatments = defaultdict(list)

    # Find the DMSO probabilities for each phenotype using the broad_sample and the well_position
    dmso_broad_filt = ((_treatment_paths["compound"]["platemap"]["broad_sample"] == "DMSO"))
    dmso_broad_wells = _treatment_paths["compound"]["platemap"].loc[dmso_broad_filt]["well_position"]

    # Rename the plate column of the barcode platemap
    _barcode_platemapdf.rename(columns={"Assay_Plate_Barcode": "Metadata_plate"}, inplace=True)

    # Store the phenotype columns
    phenotype_cols = [col for col in _probadf.columns if "Metadata" not in col]

    for model_type in _probadf["Metadata_model_type"].unique():

        filtered_model_probadf = _probadf.loc[_probadf["Metadata_model_type"] == model_type]
        dmso_probas = filtered_model_probadf.loc[filtered_model_probadf["Metadata_Well"].isin(dmso_broad_wells)][phenotype_cols]

        for treat_type_name, treat_data in _treatment_paths.items():

            # Get the data corresponding to the current treatment type
            treat_type_platemap = _barcode_platemapdf.loc[_barcode_platemapdf["Plate_Map_Name"] == treat_data["Plate_Map_Name"]]

            # Retrieve the data that correspond to the plate names, where the plate names correspond to the treatment type
            filtered_probadf = pd.merge(filtered_model_probadf, treat_type_platemap, how="inner", on="Metadata_plate")

            # Find the treatments that correspond to each well using the broad_sample
            common_broaddf = pd.merge(treat_data["metadata"], treat_data["platemap"], how="inner", on="broad_sample")
            common_broaddf = common_broaddf[["well_position", treat_data["treatment_column"], "control_type"]]

            # Iterate through plates here, then treatments
            # When iterating through plate select the negative control wells

            for utreat in common_broaddf[treat_data["treatment_column"]].unique():

                # Wells that correspond to the treatment
                treat_wells = common_broaddf.loc[common_broaddf[treat_data["treatment_column"]] == utreat]["well_position"].unique()

                # Find the treatment probabilities that correspond to each well, and therefore each treatment
                treat_probas = filtered_probadf.loc[filtered_probadf["Metadata_Well"].isin(treat_wells)]

                num_cells = len(treat_probas)

                # If there are no probability values that match the given well for some reason analyze the next treatment
                if num_cells > 0:

                    # Sample the dmso probabilities to reduce computation and make the sample sizes between groups equal
                    samp_dmsodf = dmso_probas.sample(n=num_cells, random_state=0)

                    # Iterate through each possible phenotype
                    for pheno in phenotype_cols:

                        treatments = store_comparisons(_comp_functions, treatments, samp_dmsodf[pheno], treat_probas[pheno], phenotype=pheno, treatment_type=treat_type_name, treatment=utreat, model_type=model_type, well=treat_wells.tolist(), cell_count=num_cells)

    return treatments

