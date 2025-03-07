from collections import defaultdict
from typing import Optional, Sequence, Union

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.tree import DecisionTreeRegressor, _tree


class IsoforestFeatureImportance:
    # Computes Isolation Forest (Scikit-learn) feature importances from a subset of data.

    def __init__(
        self,
        _estimators: Sequence[DecisionTreeRegressor],
        _morphology_data: pd.DataFrame,
    ):
        """
        Parameters
        ----------
        _estimators: Scikit-learn decision tree regressor estimators.
        _morphology_data: Data with only numerical morphology data (without metadata).
        """

        self._estimators = _estimators
        self._morphology_data = _morphology_data

    def save_tree_feature_importances(
        self,
        _tree_obj: _tree.Tree,
        _leaf_id: int,
        _sample_idx: int,
    ) -> dict[dict[str, float]]:
        """
        Aggregates and then returns feature importances per tree.

        Parameters
        _tree_obj: Object for traversing tree.
        _leaf_id: Leaf node for the sample in the tree.
        _sample_idx: Sample location in the dataframe.
        """

        node_id = 0  # Start at the root node
        depth = 0
        feature_importances = defaultdict(list)
        morphology_features = self._morphology_data.iloc[_sample_idx].copy()

        while node_id != _leaf_id:
            feature_idx = _tree_obj.feature[node_id]

            if feature_idx >= 0:  # Ignore leaf nodes (-2)
                feature_importances[self._morphology_data.columns[feature_idx]].append(
                    1 / (1 + depth)
                )

            if morphology_features.iloc[feature_idx] <= _tree_obj.threshold[node_id]:
                node_id = _tree_obj.children_left[node_id]
            else:
                node_id = _tree_obj.children_right[node_id]

            depth += 1

        return {
            _sample_idx: {
                feature: sum(importances) / len(importances)
                for feature, importances in feature_importances.items()
            }
        }

    def compute_isoforest_feature_importances(self) -> pd.DataFrame:
        # Computes and returns the importance for all trees and samples

        isotree_importances = Parallel(n_jobs=-1)(
            delayed(self.save_tree_feature_importances)(
                _tree_obj=estimator.tree_, _leaf_id=leaf_id, _sample_idx=sample_idx
            )
            for estimator in self._estimators
            for sample_idx, leaf_id in enumerate(
                estimator.tree_.apply(self._morphology_data.values.astype(np.float32))
            )
        )

        isoforest_importances = {}
        unique_feats = set()

        sample_isoforest_importances = {
            sample: defaultdict(list)
            for sample in range(self._morphology_data.shape[0])
        }

        # Converting data from list of tree dictionaries to dictionary of samples
        for isotree in isotree_importances:
            for sample, feature_importances in isotree.items():
                for feature, importance in feature_importances.items():
                    sample_isoforest_importances[sample][feature].append(importance)

        # Averaging feature importances per sample and feature across trees
        for sample, feature_importances in sample_isoforest_importances.items():
            isoforest_importances[sample] = defaultdict(list)
            for feature, importances in feature_importances.items():
                isoforest_importances[sample][feature] = sum(importances) / len(
                    importances
                )
                unique_feats.add(feature)

        self._isoforest_importances = pd.DataFrame(isoforest_importances).T

        return self._isoforest_importances

    def get_isoforest_importances(
        self, _features: Union[str, list[str]]
    ) -> dict[str, float]:
        """
        Return feature importances without NaNs.

        Parameters
        ----------
        _features: Morphology feature names.
        """

        _features = [_features] if isinstance(_features, str) else _features

        filtered_morphology_data = self._morphology_data[_features].copy()

        return filtered_morphology_data.apply(lambda x: x.dropna().tolist()).to_dict()
