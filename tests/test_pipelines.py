"""Tests for data pipelines"""

import numpy as np
import pandas as pd
import pytest

from src.pipelines import DataLoader, DataValidator, TaxiTripPreprocessor
from src.pipelines.exceptions import DataValidationError


@pytest.fixture
def sample_df():
    """Generate sample DataFrame"""
    np.random.seed(42)
    return pd.DataFrame(
        {
            "pickup_longitude": np.random.randn(100) * 0.1 - 74.0,
            "pickup_latitude": np.random.randn(100) * 0.1 + 40.7,
            "dropoff_longitude": np.random.randn(100) * 0.1 - 74.0,
            "dropoff_latitude": np.random.randn(100) * 0.1 + 40.7,
            "fare_amount": np.random.uniform(5, 50, 100),
        }
    )


def test_preprocessor_extract_coordinates_pickup(sample_df):
    """Test coordinate extraction for pickup"""
    coords = TaxiTripPreprocessor.extract_coordinates(
        sample_df, coordinate_type="pickup", use_location_ids=False
    )
    assert coords.shape[1] == 2  # lat, lon
    assert coords.shape[0] > 0


def test_preprocessor_extract_coordinates_both(sample_df):
    """Test coordinate extraction for both pickup and dropoff"""
    coords = TaxiTripPreprocessor.extract_coordinates(
        sample_df, coordinate_type="both", use_location_ids=False
    )
    assert coords.shape[1] == 4  # pickup_lat, pickup_lon, dropoff_lat, dropoff_lon
    assert coords.shape[0] > 0


def test_preprocessor_extract_coordinates_with_location_ids():
    """Test coordinate extraction using location IDs"""
    df = pd.DataFrame(
        {
            "PULocationID": [1, 2, 3, 4, 5],
            "DOLocationID": [10, 20, 30, 40, 50],
        }
    )
    coords = TaxiTripPreprocessor.extract_coordinates(
        df, coordinate_type="pickup", use_location_ids=True
    )
    assert coords.shape[1] == 2
    assert coords.shape[0] == 5


def test_preprocessor_filter_valid_coordinates():
    """Test coordinate filtering"""
    # Create coordinates with some invalid values
    coords = np.array(
        [
            [40.7, -74.0],  # Valid NYC coordinate
            [40.8, -73.9],  # Valid NYC coordinate
            [np.nan, -74.0],  # Invalid (NaN)
            [40.7, np.inf],  # Invalid (inf)
            [50.0, -74.0],  # Invalid (out of bounds)
        ]
    )
    filtered, mask = TaxiTripPreprocessor.filter_valid_coordinates(coords)
    assert len(filtered) == 2  # Only 2 valid coordinates
    assert mask.sum() == 2


def test_data_validator_validate_features(sample_df):
    """Test feature validation"""
    coords = TaxiTripPreprocessor.extract_coordinates(
        sample_df, coordinate_type="pickup", use_location_ids=False
    )
    # Convert to DataFrame for validation
    features_df = pd.DataFrame(coords, columns=["lat", "lon"])
    # Should not raise
    DataValidator.validate_features(features_df)


def test_data_validator_validate_features_empty():
    """Test feature validation with empty DataFrame"""
    empty_df = pd.DataFrame()
    with pytest.raises(ValueError, match="empty"):
        DataValidator.validate_features(empty_df)


def test_data_validator_validate_clustering_params():
    """Test parameter validation"""
    # Should not raise
    DataValidator.validate_clustering_params(eps=0.5, min_samples=5)

    with pytest.raises(ValueError):
        DataValidator.validate_clustering_params(eps=-1, min_samples=5)

    with pytest.raises(ValueError):
        DataValidator.validate_clustering_params(eps=0.5, min_samples=0)


def test_data_validator_get_data_stats(sample_df):
    """Test data statistics"""
    stats = DataValidator.get_data_stats(sample_df)
    assert "n_samples" in stats
    assert "n_features" in stats
    assert stats["n_samples"] == 100
    assert stats["n_features"] == 5

