"""Base adapter interface for DBSCAN implementations"""

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class BaseAdapter(ABC):
    """Base class for DBSCAN adapters"""

    @abstractmethod
    def fit_predict(
        self, X: np.ndarray, eps: float = 0.5, min_samples: int = 5, **kwargs: Any
    ) -> np.ndarray:
        """
        Fit DBSCAN model and predict cluster labels

        Args:
            X: Input data array of shape (n_samples, n_features)
            eps: Maximum distance between samples in the same neighborhood
            min_samples: Minimum number of samples in a neighborhood
            **kwargs: Additional parameters

        Returns:
            Cluster labels for each sample (-1 for noise)
        """
        pass

    @abstractmethod
    def get_params(self) -> dict[str, Any]:
        """Get adapter parameters"""
        pass

    @abstractmethod
    def get_metadata(self) -> dict[str, Any]:
        """Get adapter metadata (implementation type, version, etc.)"""
        pass

