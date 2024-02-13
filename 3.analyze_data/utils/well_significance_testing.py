from collections import defaultdict

def store_comparisons(_comp_functions, _treatments, _con_probs, _treatment_probs, **_comp_names):
    """
    Performs the comparisons between the control probabilities and the treatment probabilities.
    Stores the comparisons and the desired metadata.

    Parameters
    ----------
    _comp_functions: Dictionary of Dictionaries
        The keys are the names of the statistical tests.
        The keys of the subdictionaries are the following strings {statistical_test_function, comparison_metric}.

    _treatments: Dictionary of Lists
        The treatment results, which contains keys corresponding to the statistical test, the comparison metric, the p value, and the comparison metric value among other keys specified by comp_names.

    _con_probs: pandas.Series
        The down-sampled predicted probilities of controls for a treatment type and phenotype.
    _treatment_probs: pandas.Series
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
        results = func_data["statistical_test_function"](_con_probs, _treatment_probs)

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
    Removes wells containing less than a desired number of cells

    Parameters
    ----------
    _df: pandas.Dataframe
        The dataframe which contains the wells, which will be potentially removed

    _cutoff: Integer
        The number of cells a well must have to remain in the dataframe

    Returns
    -------
    _df: pandas.Dataframe
        The filtered dataframe with only wells that have more cells than the cutoff
    """

    # Find the number of cells in each well
    well_counts = _df["Metadata_Well"].value_counts()

    # Find the wells that contain more cells than the cutoff
    wells_kept = well_counts[well_counts > _cutoff].index

    # Keep only the wells that contain more cells than the cutoff
    _df = _df.loc[_df["Metadata_Well"].isin(wells_kept)]

    return _df

def strat_samp_wells(_welldf, _total_cell_count):
    """
    Parameters
    ----------
    _welldf: pandas.Dataframe
        The dataframe which contains the wells, which will be stratify sampled by well

    _total_cell_count: Integer
        The cell sample size

    Returns
    -------
    The sampled cells stratified by well
    """

    well_frac = _total_cell_count / _welldf.shape[0]

    def samp_well(_well_samp):
        return _well_samp.sample(frac=well_frac, random_state=0)

    return _welldf.groupby('Metadata_Well', group_keys=False).apply(samp_well)

def get_treatment_comparison(_comp_functions, _treatdf, _negcondf, _phenotype_cols, _filt_cols, _control_cutoff = 50, _treat_cutoff = 50):
    """
    This function is intended to preprocess the predicted MitoCheck phenotype probability data prior to comparing the phenotype predicted probabilities.
    Please refer to the README for additional information on how the treatment and control groups are compared.
    Parameters
    ----------
    _comp_functions: Dictionary of Dictionaries
        The keys are the names of the statistical tests.
        The keys of the subdictionaries are the following strings {statistical_test_function, comparison_metric}.
        The statistical_test_function key contains a function as a value, which outputs a zipped result of the statistical test, which must be defined prior to execution.
        The comparison_metric key contains the name of the comparison metric computed as a string.

    _treatdf: pandas.Dataframe
        The predicted probabilities and associated metadata for each treated cell (not in a control group).

    _negcondf: pandas.Dataframe
        The predicted probabilities and associated metadata for each cell in the negative control group.

    _phenotype_cols: List
        The names of the phenotype columns in the _treatdf and _negcondf dataframes.

    _filt_cols: List
        The names of the columns to group the treatment cells by before comparing the probabilities.

    _control_cutoff: Integer
        (Optional default=50) The minimum number of cells required for a negative control well to be included in the comparison.

    _treat_cutoff: Integer
        (Optional default=50) The minimum number of cells required for a treatment well (excluding negative control wells) to be included in the comparison.

    Returns
    -------
    treatments: Dictionary
        Contains the analysis information corresponding to each treatment
    """

    treatments = defaultdict(list)

    # Iterate through each group
    for filt_col_vals, group_treatdf in _treatdf.groupby(_filt_cols):

        # The columns for keeping track of metadata and filtering the negative control cells
        ref_cols = dict(zip(_filt_cols, filt_col_vals))

        # The negative control cells
        group_negdf = _negcondf.loc[(_negcondf["Metadata_Plate"] == ref_cols["Metadata_Plate"]) &
                                   (_negcondf["Metadata_model_type"] == ref_cols["Metadata_model_type"])
                                    ]

        # Remove wells if the cell count is below the corresponding threshold
        group_treatdf = filter_wells_by_cell_count(group_treatdf, _treat_cutoff)
        group_negdf = filter_wells_by_cell_count(group_negdf, _control_cutoff)

        # Compute the number of cells for each group
        treat_cell_count = len(group_treatdf)
        negcon_cell_count = len(group_negdf)
        min_cell_count = min(treat_cell_count, negcon_cell_count)

        # If there are no probability values that match the given well for some reason analyze the next treatment
        if (min_cell_count > 0):

            # Sample the treatment dataframe if the cell count for the treatments is larger than for the controls
            if treat_cell_count > negcon_cell_count:
                samp_treat = group_treatdf.sample(n=min_cell_count, random_state=0)
                samp_neg = group_negdf

            # Otherwise, keep all of the cells of the treatment group
            # Stratify sample the negative control cells by the proportion of cells in each well
            else:
                samp_treat = group_treatdf
                samp_neg = strat_samp_wells(group_negdf, min_cell_count)

            # Track the minimum cell count across all comparisons
            ref_cols["cell_count"] = min_cell_count

            # Iterate through each possible phenotype and update the treatments variable
            for pheno in _phenotype_cols:
                ref_cols["phenotype"] = pheno
                treatments = store_comparisons(_comp_functions, treatments, samp_neg[pheno], samp_treat[pheno], **ref_cols)

    return treatments
