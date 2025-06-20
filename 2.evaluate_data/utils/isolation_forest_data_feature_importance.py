from collections import defaultdict
from typing import Optional, Union

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.tree import DecisionTreeRegressor, _tree


class IsoforestFeatureImportance:
    """
    Computes Isolation Forest (Scikit-learn) feature importances from a subset of data.
    Feature importances were derived from the Isolation Forest paper.
    See https://doi.org/10.1109/ICDM.2008.17 for more details.
    This approach assumes each feature between a sample's leaf node and root node
    is equally important in isolating that sample for a given isolation tree estimator.
    """

    def __init__(
        self,
        estimators: list[DecisionTreeRegressor],
        morphology_data: pd.DataFrame,
        num_train_samples_per_tree: int,
    ):
        """
        Parameters
        ----------
        _estimators: Scikit-learn decision tree regressor estimators.
        _morphology_data: Data with only numerical morphology data (without metadata).
        """

        self._estimators = estimators
        self._morphology_data = morphology_data
        self._isoforest_importances = None
        self._norm_factor = self._compute_norm_factor(
            _num_features_per_forest=num_train_samples_per_tree
        )

    @property
    def isoforest_importances(self) -> pd.DataFrame:
        if self._isoforest_importances is None:
            raise ValueError("isoforest_importances have not been computed")

        return self._isoforest_importances

    def _compute_norm_factor(self, _num_features_per_forest: int) -> float:
        """
        Used to compute the anomaly score in an isolation forest.
        """

        harmonic_approx = np.log(_num_features_per_forest - 1) + np.euler_gamma

        return (
            2 * harmonic_approx
            - 2 * (_num_features_per_forest - 1) / _num_features_per_forest
        )

    def save_tree_feature_depths(
        self,
        _tree_obj: _tree.Tree,
        _leaf_id: int,
        _sample_idx: int,
    ) -> dict[dict[str, float]]:
        """
        Returns sample depths per feature.

        Parameters
        _tree_obj: Object for traversing tree.
        _leaf_id: Leaf node for the sample in the tree.
        _sample_idx: Sample location in the dataframe.
        """

        node_id = 0  # Start at the root node
        depth = 0
        num_features = defaultdict(int)
        morphology_features = self._morphology_data.iloc[_sample_idx].copy()

        while node_id != _leaf_id:
            feature_idx = _tree_obj.feature[node_id]

            if feature_idx >= 0:  # Ignore leaf nodes (-2)
                # Indicates if a feature is present in a tree (1)
                num_features[self._morphology_data.columns[feature_idx]] += 1

            if morphology_features.iloc[feature_idx] <= _tree_obj.threshold[node_id]:
                node_id = _tree_obj.children_left[node_id]
            else:
                node_id = _tree_obj.children_right[node_id]

            depth += 1

        if node_id != _leaf_id:
            return {
                _sample_idx: {feature: [depth] * count}
                for feature, count in num_features.items()
            }

    def compute_isoforest_importances(self: Self) -> pd.DataFrame:
        # Computes feature importances for all features and samples (if they exist) using lazy parallelization.

        isotree_sample_importances = Parallel(n_jobs=-1)(
            delayed(self.save_tree_feature_depths)(
                _tree_obj=estimator.tree_, _leaf_id=leaf_id, _sample_idx=sample_idx
            )
            for estimator in self._estimators
            for sample_idx, leaf_id in enumerate(
                estimator.tree_.apply(self._morphology_data.values.astype(np.float32))
            )
        )

        isotree_sample_importances = [
            tree_sample
            for tree_sample in isotree_sample_importances
            if tree_sample is not None
        ]

        sample_isoforest_importances = defaultdict(lambda: defaultdict(list))

        # Converting data from list of tree dictionaries to dictionary of samples
        for isotree_sample in isotree_sample_importances:
            for sample, sample_isotree_feature_counts in isotree_sample.items():
                for feature, depths in sample_isotree_feature_counts.items():
                    sample_isoforest_importances[sample][feature].extend(depths)

        isoforest_importances = defaultdict(lambda: dict)

        # Computes the feature importance across all trees that
        # split using the corresponding feature.
        # This is similar to the anomaly score for samples, but for
        # each (sample,feature) pair.
        for (
            sample,
            sample_isotree_feature_counts,
        ) in sample_isoforest_importances.items():
            for feature, depths in sample_isotree_feature_counts.items():
                num_features = len(depths)

                isoforest_importances[sample][feature] = np.prod(
                    [
                        2 ** -(depth / (num_features * self._norm_factor))
                        for depth in depths
                    ]
                )

        self._isoforest_importances = pd.DataFrame(isoforest_importances).T

        return self._isoforest_importances

    def get_filtered_isoforest_importances(
        self, features: Union[str, list[str]]
    ) -> dict[str, float]:
        """
        Return feature importances without NaNs.

        Parameters
        ----------
        _features: Morphology feature names.
        """

        features = [features] if isinstance(features, str) else features

        if self._isoforest_importances is None:
            filtered_morphology_data = self.compute_isoforest_importances()

        else:
            filtered_morphology_data = self._isoforest_importances[features].copy()

        return filtered_morphology_data.apply(lambda x: x.dropna().tolist()).to_dict()

    def __call__(self) -> pd.DataFrame:
        # Return the final dataframe (likely with NaNs)
        return self.compute_isoforest_importances()
