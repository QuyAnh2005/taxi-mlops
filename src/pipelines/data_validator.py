"""Data validation utilities"""

from typing import Any

import numpy as np
import pandas as pd


class DataValidator:
    """Validate data for clustering"""

    @staticmethod
    def validate_features(df: pd.DataFrame) -> None:
        """
        Validate feature DataFrame

        Args:
            df: Feature DataFrame to validate

        Raises:
            ValueError: If validation fails
        """
        if df.empty:
            raise ValueError("Feature DataFrame is empty")

        if df.isnull().any().any():
            raise ValueError("Feature DataFrame contains NaN values")

        if np.isinf(df.select_dtypes(include=[np.number])).any().any():
            raise ValueError("Feature DataFrame contains infinite values")

        if len(df.columns) == 0:
            raise ValueError("Feature DataFrame has no columns")

    @staticmethod
    def validate_clustering_params(eps: float, min_samples: int) -> None:
        """
        Validate DBSCAN parameters

        Args:
            eps: Maximum distance between samples
            min_samples: Minimum number of samples

        Raises:
            ValueError: If validation fails
        """
        if eps <= 0:
            raise ValueError(f"eps must be positive, got {eps}")

        if min_samples < 1:
            raise ValueError(f"min_samples must be at least 1, got {min_samples}")

    @staticmethod
    def get_data_stats(df: pd.DataFrame) -> dict[str, Any]:
        """
        Get statistics about the data

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with data statistics
        """
        return {
            "n_samples": len(df),
            "n_features": len(df.columns),
            "feature_names": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2,
        }

