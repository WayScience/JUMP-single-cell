import warnings

import pandas as pd
from farmhash import Fingerprint64


class DeterministicSampling:

    def __init__(
        self,
        _platedf: pd.DataFrame,
        _samples_per_plate: int,
        _plate_column: str,
        _well_column: str,
        _cell_id_columns: list[str],
    ):
        self._platedf = _platedf
        self._samples_per_plate = _samples_per_plate
        self._plate_column = _plate_column
        self._well_column = _well_column
        self._cell_id_columns = _cell_id_columns
        self._divisor = 10_000

    """
    _plate_column, _well_column and _cell_id_columns must be present in _platedf.
    _cell_id_columns will be used with _plate_column and _well_column to uniquely identify each cell.
    For example, _cell_id_columns in some projects could be ["Metadata_Site", "Metadata_ObjectNumber"]
    """

    @property
    def platedf(self):
        return self._platedf.copy()

    def __hash_data(self):
        hash_cols = [self._plate_column, self._well_column]
        self._group_cols = hash_cols.copy()

        hash_cols += self._cell_id_columns

        self._platedf["Metadata_farmhash"] = self._platedf.apply(
            lambda row: Fingerprint64("".join(str(row[col]) for col in hash_cols))
            % self._divisor,
            axis=1,
        )

    def sample_plate_deterministically(self, _sample_strategy: str = "well_sampling"):
        """
        _sample_strategy can be one of the following:
            "well_sampling": Approximately samples a fixed number of samples per well based on self._samples_per_plate
            "plate_sampling": Approximately samples self._samples_per_plate from the plate.
        """
        self.__hash_data()

        if _sample_strategy != "well_sampling":
            mod_cutoff = (
                self._samples_per_plate / self._platedf.shape[0]
            ) * self._divisor
            return self._platedf.loc[self._platedf["Metadata_farmhash"] < mod_cutoff]

        grouped_platedf = self._platedf.groupby(self._group_cols)

        num_groups = len(grouped_platedf.groups)

        # Samples approximately this number, per group, from the plate dataframe self._platedf
        samples_per_group = self._samples_per_plate // num_groups

        if samples_per_group < 1:
            warnings.warn(
                "The number of samples per group must be at least 1. Changing this to 1."
            )
            samples_per_plate = 1

        sampled_platedf = []

        for _, group_df in grouped_platedf:
            num_samples_group = group_df.shape[0]
            mod_cutoff = (samples_per_group / num_samples_group) * self._divisor
            sampled_platedf.append(
                group_df.loc[group_df["Metadata_farmhash"] < mod_cutoff]
            )

        return pd.concat(sampled_platedf, axis=0)
