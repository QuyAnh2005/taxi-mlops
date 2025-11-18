"""Standard sequential DBSCAN adapter using scikit-learn"""

from typing import Any

import numpy as np
from sklearn.cluster import DBSCAN

from .base_adapter import BaseAdapter


class SklearnAdapter(BaseAdapter):
    """Standard sequential DBSCAN implementation using scikit-learn"""

    def __init__(self, **kwargs: Any):
        """
        Initialize the sklearn DBSCAN adapter

        Args:
            **kwargs: Additional parameters for DBSCAN
        """
        self.kwargs = kwargs
        self.model: DBSCAN | None = None

    def fit_predict(
        self, X: np.ndarray, eps: float = 0.5, min_samples: int = 5, **kwargs: Any
    ) -> np.ndarray:
        """
        Fit DBSCAN model and predict cluster labels

        Args:
            X: Input data array of shape (n_samples, n_features)
            eps: Maximum distance between samples in the same neighborhood
            min_samples: Minimum number of samples in a neighborhood
            **kwargs: Additional parameters merged with initialization kwargs

        Returns:
            Cluster labels for each sample (-1 for noise)
        """
        merged_kwargs = {**self.kwargs, **kwargs}
        self.model = DBSCAN(eps=eps, min_samples=min_samples, **merged_kwargs)
        labels = self.model.fit_predict(X)
        return labels

    def get_params(self) -> dict[str, Any]:
        """Get adapter parameters"""
        if self.model is None:
            return {"eps": None, "min_samples": None, **self.kwargs}
        return {
            "eps": self.model.eps,
            "min_samples": self.model.min_samples,
            "metric": self.model.metric,
            "algorithm": self.model.algorithm,
            **self.kwargs,
        }

    def get_metadata(self) -> dict[str, Any]:
        """Get adapter metadata"""
        return {
            "adapter_type": "sklearn",
            "implementation": "sequential",
            "version": "1.3.0",
            "description": "Standard sequential DBSCAN using scikit-learn",
        }

