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
    _plate_column, _well_column and _cell_id_columns store column names, and must be present in _platedf.
    _cell_id_columns will be used with _plate_column and _well_column to uniquely identify each cell.
    For example, _cell_id_columns in some projects could be ["Metadata_Site", "Metadata_ObjectNumber"]
    """

    @property
    def platedf(self):
        return self._platedf.copy()

    def __hash_data(self):
        # Create a hash for each data entry

        hash_cols = [self._plate_column, self._well_column] + self._cell_id_columns
        self._group_cols = hash_cols[0:2]

        combined_strs = self._platedf[hash_cols].astype(str).agg("".join, axis=1)

        # Vectorized hash mapping
        self._platedf["Metadata_farmhash"] = combined_strs.map(
            lambda x: Fingerprint64(x) % self._divisor
        )

    def sample_plate_deterministically(self, _sample_strategy: str = "well_sampling"):
        self.__hash_data()

        if _sample_strategy != "well_sampling":
            mod_cutoff = (
                self._samples_per_plate / self._platedf.shape[0]
            ) * self._divisor
            return self._platedf.loc[self._platedf["Metadata_farmhash"] < mod_cutoff]

        grouped = self._platedf.groupby(self._group_cols)

        num_groups = len(grouped)
        samples_per_group = max(1, self._samples_per_plate // num_groups)

        # Fixed sampling per group using hash
        return pd.concat(
            (
                group_df.loc[
                    group_df["Metadata_farmhash"]
                    < (samples_per_group / len(group_df)) * self._divisor
                ]
                for _, group_df in grouped
            ),
            ignore_index=True,
        )
