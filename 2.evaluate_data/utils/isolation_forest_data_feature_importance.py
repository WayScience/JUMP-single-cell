# Learn more about the methods used in this module
# by reading the isolation forest paper:
# https://doi.org/10.1109/ICDM.2008.17

from typing import Iterable, Optional, Union

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.tree import DecisionTreeRegressor, _tree


def isoforest_expected_length(node_sample_counts: np.ndarray) -> np.ndarray:
    """
    Compute expected path length c(n) for an array of node sizes, where c(n)
    is the average path length of an unsuccessful Binary Search Tree (BST) search (same as the
    iForest remaining-path normalizer and leaf correction term).

    Parameters
    ----------
    node_sample_counts : np.ndarray
        Number of training samples in each node.

    Returns
    -------
    np.ndarray
        Expected path length for each input node size.
    """

    node_sample_counts = np.asarray(node_sample_counts)
    out = np.zeros_like(node_sample_counts, dtype=float)
    mask_1 = node_sample_counts <= 1
    mask_2 = node_sample_counts == 2
    mask_rest = ~(mask_1 | mask_2)

    out[mask_1] = 0.0
    out[mask_2] = 1.0
    remaining_node_counts = node_sample_counts[mask_rest].astype(float)

    # This equation came from the paper to compute c(n)
    out[mask_rest] = 2.0 * (
        np.log(remaining_node_counts - 1.0) + np.euler_gamma
    ) - 2.0 * ((remaining_node_counts - 1.0) / remaining_node_counts)

    return out


class IsoforestFeatureImportance:
    """
    Per-sample Isolation Forest feature contributions using split gain.
    For each point x and tree t, contributions sum the split gains
    g(v, x) = c(n_p) - [1 + c(n_c)] along the path x takes, then
    average over trees.
    Higher values indicate a feature was more important for isolating a sample.
    """

    def __init__(
        self,
        estimators: list[DecisionTreeRegressor],
        morphology_data: pd.DataFrame,
        estimators_features: Optional[Iterable[np.ndarray]] = None,
    ):
        """
        Parameters
        ----------
        estimators : list[DecisionTreeRegressor]
            Fitted isolation trees (e.g., from IsolationForest.estimators_).
        morphology_data : pd.DataFrame
            Feature matrix to explain; columns must match the model features.
        estimators_features : Iterable[np.ndarray] | None
            Optional per-tree feature index subsets (IsolationForest.estimators_features_).
        """

        self._estimators = estimators
        self._estimators_features = estimators_features
        self._morphology_data = morphology_data
        self._isoforest_importances = None

    @property
    def isoforest_importances(self) -> pd.DataFrame:
        if self._isoforest_importances is None:
            raise ValueError("isoforest_importances have not been computed")

        return self._isoforest_importances

    def _compute_tree_gains(
        self,
        estimator: DecisionTreeRegressor,
        X_data: np.ndarray,
        feat_subset: np.ndarray,
    ) -> np.ndarray:
        """
        Compute per-sample, per-feature gains for a single tree.

        Parameters
        ----------
        estimator : DecisionTreeRegressor
            The fitted isolation tree to traverse.
        X_data : np.ndarray
            Feature matrix (float) aligned to the model's feature order.
        feat_subset : np.ndarray
            Global feature indices used by this tree (from estimators_features_).

        Returns
        -------
        np.ndarray
            Array of shape (n_samples, n_features) with split-gain contributions
            for this tree.
        """

        tree = estimator.tree_
        num_samples, _ = X_data.shape

        left_children = tree.children_left
        right_children = tree.children_right
        tree_feats = tree.feature
        feat_thresholds = tree.threshold

        node_lengths = isoforest_expected_length(tree.n_node_samples)
        total_tree_gain = np.zeros_like(X_data, dtype=float)

        for sample_idx in range(num_samples):
            sample_node = 0
            while tree_feats[sample_node] != _tree.TREE_UNDEFINED:
                tree_feat_idx = tree_feats[sample_node]
                rel_feat_idx = feat_subset[tree_feat_idx]

                if X_data[sample_idx, rel_feat_idx] <= feat_thresholds[sample_node]:
                    child = left_children[sample_node]
                else:
                    child = right_children[sample_node]

                # Subtracting 1, because the expected path length is one less
                # once the next step was taken (to the child node).
                # The child node will sometimes be a leaf node as some samples may
                # not be isolated.
                sample_tree_gain = node_lengths[sample_node] - 1.0 - node_lengths[child]
                total_tree_gain[sample_idx, rel_feat_idx] += sample_tree_gain
                sample_node = child

        return total_tree_gain

    def compute_isoforest_importances(self) -> pd.DataFrame:
        """
        Compute per-sample, per-feature split-gain contributions averaged over trees.

        Returns
        -------
        pd.DataFrame
            DataFrame of averaged contributions with sample index matching
            `morphology_data` and columns matching feature names.
        """

        feature_names = list(self._morphology_data.columns)
        X = self._morphology_data[feature_names].to_numpy(dtype=float, copy=False)

        feat_subsets: list[np.ndarray] = (
            [np.asarray(fs, dtype=int) for fs in self._estimators_features]
            if self._estimators_features is not None
            else [np.arange(X.shape[1], dtype=int)] * len(self._estimators)
        )

        average_tree_gains = np.zeros_like(X, dtype=float)

        all_tree_gains = Parallel(n_jobs=-1)(
            delayed(self._compute_tree_gains)(estimator, X, subset)
            for estimator, subset in zip(self._estimators, feat_subsets)
        )

        for total_tree_gain in all_tree_gains:
            average_tree_gains += total_tree_gain

        average_tree_gains /= len(self._estimators)

        self._isoforest_importances = pd.DataFrame(
            average_tree_gains, columns=feature_names, index=self._morphology_data.index
        )

        return self._isoforest_importances

    def get_filtered_isoforest_importances(
        self, features: Union[str, list[str]]
    ) -> dict[str, list[float]]:
        """
        Return feature importances without NaNs.

        Parameters
        ----------
        features: Morphology feature names.

        Returns
        -------
        dict[str, list[float]]
            A mapping from feature name to a list of non-NaN importance values.
        """

        features = [features] if isinstance(features, str) else features

        if self._isoforest_importances is None:
            filtered_morphology_data = self.compute_isoforest_importances()
        else:
            filtered_morphology_data = self._isoforest_importances[features].copy()

        return filtered_morphology_data.apply(lambda x: x.dropna().tolist()).to_dict()

    def __call__(self) -> pd.DataFrame:
        """Compute or return cached per-sample, per-feature importances."""

        return self.compute_isoforest_importances()
