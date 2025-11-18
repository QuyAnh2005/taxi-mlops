"""Quality metrics for evaluating clustering results"""

from typing import Any

import numpy as np
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)


class QualityMetrics:
    """Compute quality metrics for clustering results"""

    @staticmethod
    def compute_silhouette_score(X: np.ndarray, labels: np.ndarray) -> float:
        """
        Compute silhouette score

        Args:
            X: Feature array
            labels: Cluster labels

        Returns:
            Silhouette score (-1 to 1, higher is better)
        """
        if len(np.unique(labels)) < 2:
            return -1.0  # Need at least 2 clusters

        # Remove noise points for silhouette calculation
        valid_mask = labels != -1
        if valid_mask.sum() < 2:
            return -1.0

        X_valid = X[valid_mask]
        labels_valid = labels[valid_mask]

        if len(np.unique(labels_valid)) < 2:
            return -1.0

        try:
            return float(
                silhouette_score(X_valid, labels_valid, sample_size=min(10000, len(X_valid)))
            )
        except Exception:
            return -1.0

    @staticmethod
    def compute_davies_bouldin_score(X: np.ndarray, labels: np.ndarray) -> float:
        """
        Compute Davies-Bouldin index

        Args:
            X: Feature array
            labels: Cluster labels

        Returns:
            Davies-Bouldin score (lower is better)
        """
        # Remove noise points
        valid_mask = labels != -1
        if valid_mask.sum() < 2:
            return float("inf")

        X_valid = X[valid_mask]
        labels_valid = labels[valid_mask]

        if len(np.unique(labels_valid)) < 2:
            return float("inf")

        try:
            return float(davies_bouldin_score(X_valid, labels_valid))
        except Exception:
            return float("inf")

    @staticmethod
    def compute_calinski_harabasz_score(X: np.ndarray, labels: np.ndarray) -> float:
        """
        Compute Calinski-Harabasz index (Variance Ratio Criterion)

        Args:
            X: Feature array
            labels: Cluster labels

        Returns:
            Calinski-Harabasz score (higher is better)
        """
        # Remove noise points
        valid_mask = labels != -1
        if valid_mask.sum() < 2:
            return 0.0

        X_valid = X[valid_mask]
        labels_valid = labels[valid_mask]

        if len(np.unique(labels_valid)) < 2:
            return 0.0

        try:
            return float(calinski_harabasz_score(X_valid, labels_valid))
        except Exception:
            return 0.0

    @staticmethod
    def compute_adjusted_rand_score(
        labels_true: np.ndarray, labels_pred: np.ndarray
    ) -> float:
        """
        Compute Adjusted Rand Index for comparing two clusterings

        Args:
            labels_true: True cluster labels
            labels_pred: Predicted cluster labels

        Returns:
            Adjusted Rand Index (-1 to 1, higher is better)
        """
        try:
            return float(adjusted_rand_score(labels_true, labels_pred))
        except Exception:
            return -1.0

    @staticmethod
    def compute_cluster_statistics(labels: np.ndarray) -> dict[str, Any]:
        """
        Compute basic cluster statistics

        Args:
            labels: Cluster labels

        Returns:
            Dictionary with cluster statistics
        """
        unique_labels = np.unique(labels)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        n_noise = np.sum(labels == -1)
        n_samples = len(labels)

        # Cluster sizes
        cluster_sizes = []
        for label in unique_labels:
            if label != -1:
                cluster_sizes.append(np.sum(labels == label))

        return {
            "n_clusters": int(n_clusters),
            "n_noise": int(n_noise),
            "n_samples": int(n_samples),
            "noise_ratio": float(n_noise / n_samples) if n_samples > 0 else 0.0,
            "cluster_sizes": cluster_sizes,
            "avg_cluster_size": (
                float(np.mean(cluster_sizes)) if cluster_sizes else 0.0
            ),
            "min_cluster_size": (
                int(np.min(cluster_sizes)) if cluster_sizes else 0
            ),
            "max_cluster_size": (
                int(np.max(cluster_sizes)) if cluster_sizes else 0
            ),
        }

    @staticmethod
    def compute_all_quality_metrics(
        X: np.ndarray, labels: np.ndarray
    ) -> dict[str, Any]:
        """
        Compute all quality metrics for clustering results

        Args:
            X: Feature array
            labels: Cluster labels

        Returns:
            Dictionary with all quality metrics
        """
        metrics = {}

        # Cluster statistics
        cluster_stats = QualityMetrics.compute_cluster_statistics(labels)
        metrics.update(cluster_stats)

        # Quality scores
        metrics["silhouette_score"] = QualityMetrics.compute_silhouette_score(X, labels)
        metrics["davies_bouldin_score"] = QualityMetrics.compute_davies_bouldin_score(
            X, labels
        )
        metrics["calinski_harabasz_score"] = (
            QualityMetrics.compute_calinski_harabasz_score(X, labels)
        )

        return metrics

    @staticmethod
    def compare_clusterings(
        labels1: np.ndarray, labels2: np.ndarray
    ) -> dict[str, Any]:
        """
        Compare two clusterings

        Args:
            labels1: First clustering labels
            labels2: Second clustering labels

        Returns:
            Dictionary with comparison metrics
        """
        return {
            "adjusted_rand_index": QualityMetrics.compute_adjusted_rand_score(
                labels1, labels2
            ),
            "n_clusters_1": len(np.unique(labels1)) - (1 if -1 in labels1 else 0),
            "n_clusters_2": len(np.unique(labels2)) - (1 if -1 in labels2 else 0),
            "n_noise_1": int(np.sum(labels1 == -1)),
            "n_noise_2": int(np.sum(labels2 == -1)),
        }

