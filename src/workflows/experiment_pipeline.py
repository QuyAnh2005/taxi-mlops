"""Prefect workflow for DBSCAN experiments"""

import time
import uuid
from typing import Any

import mlflow
import numpy as np
import pandas as pd
from prefect import flow, task

from ..adapters import SklearnAdapter, SklearnParallelAdapter
from ..config import settings
from ..monitoring import MetricsCollector, record_flow_metrics
from ..pipelines import DataLoader, DataValidator, TaxiTripPreprocessor
from ..storage import MinIOClient, PostgresClient


@task(name="load_data")
def load_data_task(data_source: str, use_minio: bool = True) -> pd.DataFrame:
    """
    Load data from MinIO or local file

    Args:
        data_source: Object name in MinIO or local file path
        use_minio: If True, load from MinIO first (default: True)

    Returns:
        Loaded DataFrame
    """
    if use_minio:
        return DataLoader.load_data(data_source)
    else:
        return DataLoader.load_from_file(data_source)


@task(name="prepare_features")
def prepare_features_task(
    df: pd.DataFrame,
    coordinate_type: str = "pickup",
    use_location_ids: bool = True,
) -> np.ndarray:
    """
    Prepare features for clustering by extracting coordinates

    Args:
        df: Input DataFrame
        coordinate_type: Type of coordinates to extract ('pickup' or 'dropoff')
            Note: Only 2D coordinates (pickup or dropoff) are used for clustering
        use_location_ids: If True, use location IDs when coordinates not available

    Returns:
        Array of coordinates ready for clustering (shape: n_samples, 2)
    """
    # Extract coordinates using the preprocessor
    coords = TaxiTripPreprocessor.extract_coordinates(
        df, coordinate_type=coordinate_type, use_location_ids=use_location_ids
    )

    # Filter valid coordinates (bounds checking)
    coords, valid_mask = TaxiTripPreprocessor.filter_valid_coordinates(coords)

    if len(coords) == 0:
        raise ValueError("No valid coordinates found after filtering.")

    return coords


@task(name="run_experiment")
def run_experiment_task(
    adapter_type: str,
    X: np.ndarray,
    eps: float,
    min_samples: int,
    experiment_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Run DBSCAN experiment

    Args:
        adapter_type: Type of adapter ('sklearn' or 'sklearn_parallel')
        X: Feature array
        eps: DBSCAN eps parameter
        min_samples: DBSCAN min_samples parameter
        experiment_id: Unique experiment ID
        **kwargs: Additional parameters

    Returns:
        Dictionary with results and metrics
    """
    # Initialize adapter
    if adapter_type == "sklearn":
        adapter = SklearnAdapter(**kwargs)
    elif adapter_type == "sklearn_parallel":
        n_jobs = kwargs.pop("n_jobs", -1)
        adapter = SklearnParallelAdapter(n_jobs=n_jobs, **kwargs)
    else:
        raise ValueError(f"Unknown adapter type: {adapter_type}")

    # Run clustering
    start_time = time.time()
    labels = adapter.fit_predict(X, eps=eps, min_samples=min_samples)
    elapsed_time = time.time() - start_time

    # Calculate metrics
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    n_samples = len(labels)

    metrics = {
        "n_clusters": n_clusters,
        "n_noise": n_noise,
        "n_samples": n_samples,
        "noise_ratio": n_noise / n_samples if n_samples > 0 else 0.0,
        "elapsed_time_seconds": elapsed_time,
    }

    params = adapter.get_params()
    metadata = adapter.get_metadata()

    return {
        "experiment_id": experiment_id,
        "adapter_type": adapter_type,
        "labels": labels,
        "metrics": metrics,
        "parameters": params,
        "metadata": metadata,
    }


@task(name="log_to_mlflow")
def log_to_mlflow_task(
    experiment_id: str,
    adapter_type: str,
    metrics: dict[str, Any],
    parameters: dict[str, Any],
    metadata: dict[str, Any],
) -> None:
    """
    Log experiment to MLflow

    Args:
        experiment_id: Experiment ID
        adapter_type: Adapter type
        metrics: Experiment metrics
        parameters: Experiment parameters
        metadata: Adapter metadata
    """
    import os

    # Set AWS credentials for MinIO/S3 access
    os.environ["AWS_ACCESS_KEY_ID"] = settings.aws_access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = settings.aws_secret_access_key
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = settings.mlflow_s3_endpoint_url

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.experiment_name)

    with mlflow.start_run(run_name=f"{adapter_type}_{experiment_id}"):
        mlflow.log_params(parameters)
        mlflow.log_metrics(metrics)
        mlflow.log_dict(metadata, "metadata.json")


@task(name="save_to_postgres")
def save_to_postgres_task(
    experiment_id: str,
    adapter_type: str,
    parameters: dict[str, Any],
    metrics: dict[str, Any],
) -> None:
    """
    Save experiment metadata to PostgreSQL

    Args:
        experiment_id: Experiment ID
        adapter_type: Adapter type
        parameters: Experiment parameters
        metrics: Experiment metrics
    """
    postgres_client = PostgresClient()
    postgres_client.save_experiment(experiment_id, adapter_type, parameters, metrics)


@flow(name="experiment_pipeline", log_prints=True)
def experiment_pipeline(
    data_source: str,
    adapter_type: str = "sklearn",
    eps: float = 0.5,
    min_samples: int = 5,
    coordinate_type: str = "pickup",
    use_location_ids: bool = True,
    max_samples: int | None = None,
    use_minio: bool = True,
    experiment_id: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Main experiment pipeline flow

    Args:
        data_source: Object name in MinIO or local file path
        adapter_type: Type of adapter ('sklearn' or 'sklearn_parallel')
        eps: DBSCAN eps parameter
        min_samples: DBSCAN min_samples parameter
        coordinate_type: Type of coordinates to extract ('pickup' or 'dropoff')
            Note: Only 2D coordinates are used for clustering, not 'both'
        use_location_ids: If True, use location IDs when coordinates not available
        max_samples: Maximum number of samples to use (for testing, None = use all)
        use_minio: If True, load from MinIO first (default: True)
        experiment_id: Experiment ID (auto-generated if not provided)
        **kwargs: Additional parameters for adapters

    Returns:
        Dictionary with experiment results
    """
    import time
    
    flow_start_time = time.time()
    if experiment_id is None:
        experiment_id = str(uuid.uuid4())

    try:
        # Validate parameters
        DataValidator.validate_clustering_params(eps, min_samples)
        
        # Validate coordinate_type - only allow pickup or dropoff (2D coordinates)
        if coordinate_type not in ["pickup", "dropoff"]:
            raise ValueError(
                f"coordinate_type must be 'pickup' or 'dropoff', got '{coordinate_type}'. "
                "Only 2D coordinates are used for clustering."
            )

        # Collect metrics
        with MetricsCollector(adapter_type, experiment_id):
            # Load and prepare data
            df = load_data_task(data_source, use_minio=use_minio)
            # Sample data if max_samples is specified (for testing)
            if max_samples is not None and len(df) > max_samples:
                df = df.sample(max_samples, random_state=42)

            # Extract coordinates using preprocessor
            X = prepare_features_task(df, coordinate_type=coordinate_type, use_location_ids=use_location_ids)

            # Run experiment
            result = run_experiment_task(
                adapter_type, X, eps, min_samples, experiment_id, **kwargs
            )

            # Log to MLflow
            log_to_mlflow_task(
                experiment_id,
                result["adapter_type"],
                result["metrics"],
                result["parameters"],
                result["metadata"],
            )

            # Save to PostgreSQL
            save_to_postgres_task(
                experiment_id,
                result["adapter_type"],
                result["parameters"],
                result["metrics"],
            )

        # Record flow metrics
        flow_duration = time.time() - flow_start_time
        record_flow_metrics("experiment_pipeline", flow_duration, True)

        return result
    except Exception as e:
        # Record failed flow
        flow_duration = time.time() - flow_start_time
        record_flow_metrics("experiment_pipeline", flow_duration, False)
        raise

