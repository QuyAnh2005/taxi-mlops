"""Parallel DBSCAN adapter using scikit-learn with joblib"""

from typing import Any

import numpy as np
from sklearn.cluster import DBSCAN

from .base_adapter import BaseAdapter


class SklearnParallelAdapter(BaseAdapter):
    """Parallel DBSCAN implementation using scikit-learn with joblib"""

    def __init__(self, n_jobs: int = -1, **kwargs: Any):
        """
        Initialize the parallel sklearn DBSCAN adapter

        Args:
            n_jobs: Number of parallel jobs (-1 means use all processors)
            **kwargs: Additional parameters for DBSCAN
        """
        self.n_jobs = n_jobs
        self.kwargs = kwargs
        self.model: DBSCAN | None = None

    def fit_predict(
        self, X: np.ndarray, eps: float = 0.5, min_samples: int = 5, **kwargs: Any
    ) -> np.ndarray:
        """
        Fit DBSCAN model and predict cluster labels using parallel processing

        Args:
            X: Input data array of shape (n_samples, n_features)
            eps: Maximum distance between samples in the same neighborhood
            min_samples: Minimum number of samples in a neighborhood
            **kwargs: Additional parameters merged with initialization kwargs

        Returns:
            Cluster labels for each sample (-1 for noise)
        """
        merged_kwargs = {**self.kwargs, **kwargs}
        self.model = DBSCAN(
            eps=eps, min_samples=min_samples, n_jobs=self.n_jobs, **merged_kwargs
        )
        labels = self.model.fit_predict(X)
        return labels

    def get_params(self) -> dict[str, Any]:
        """Get adapter parameters"""
        if self.model is None:
            return {
                "eps": None,
                "min_samples": None,
                "n_jobs": self.n_jobs,
                **self.kwargs,
            }
        return {
            "eps": self.model.eps,
            "min_samples": self.model.min_samples,
            "metric": self.model.metric,
            "algorithm": self.model.algorithm,
            "n_jobs": self.n_jobs,
            **self.kwargs,
        }

    def get_metadata(self) -> dict[str, Any]:
        """Get adapter metadata"""
        return {
            "adapter_type": "sklearn_parallel",
            "implementation": "parallel",
            "version": "1.3.0",
            "description": "Parallel DBSCAN using scikit-learn with joblib",
            "n_jobs": self.n_jobs,
        }

