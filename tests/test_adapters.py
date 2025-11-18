"""Tests for DBSCAN adapters"""

import numpy as np
import pytest

from src.adapters import SklearnAdapter, SklearnParallelAdapter


@pytest.fixture
def sample_data():
    """Generate sample data for testing"""
    np.random.seed(42)
    # Create two distinct clusters
    cluster1 = np.random.randn(50, 2) + np.array([2, 2])
    cluster2 = np.random.randn(50, 2) + np.array([-2, -2])
    noise = np.random.randn(10, 2) * 0.5
    return np.vstack([cluster1, cluster2, noise])


def test_sklearn_adapter(sample_data):
    """Test sequential sklearn adapter"""
    adapter = SklearnAdapter()
    labels = adapter.fit_predict(sample_data, eps=1.0, min_samples=5)

    assert len(labels) == len(sample_data)
    assert isinstance(labels, np.ndarray)
    assert len(set(labels)) > 0  # At least one cluster or noise

    params = adapter.get_params()
    assert "eps" in params
    assert "min_samples" in params

    metadata = adapter.get_metadata()
    assert metadata["adapter_type"] == "sklearn"
    assert metadata["implementation"] == "sequential"


def test_sklearn_parallel_adapter(sample_data):
    """Test parallel sklearn adapter"""
    adapter = SklearnParallelAdapter(n_jobs=2)
    labels = adapter.fit_predict(sample_data, eps=1.0, min_samples=5)

    assert len(labels) == len(sample_data)
    assert isinstance(labels, np.ndarray)
    assert len(set(labels)) > 0

    params = adapter.get_params()
    assert "eps" in params
    assert "min_samples" in params
    assert "n_jobs" in params

    metadata = adapter.get_metadata()
    assert metadata["adapter_type"] == "sklearn_parallel"
    assert metadata["implementation"] == "parallel"


def test_adapters_consistency(sample_data):
    """Test that both adapters produce similar results"""
    adapter_seq = SklearnAdapter()
    adapter_par = SklearnParallelAdapter(n_jobs=2)

    labels_seq = adapter_seq.fit_predict(sample_data, eps=1.0, min_samples=5)
    labels_par = adapter_par.fit_predict(sample_data, eps=1.0, min_samples=5)

    # Both should produce the same number of clusters (allowing for minor differences)
    n_clusters_seq = len(set(labels_seq)) - (1 if -1 in labels_seq else 0)
    n_clusters_par = len(set(labels_par)) - (1 if -1 in labels_par else 0)

    # Results should be similar (within 1 cluster difference due to parallelization)
    assert abs(n_clusters_seq - n_clusters_par) <= 1

