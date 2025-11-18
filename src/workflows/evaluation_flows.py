"""Prefect workflows for automated evaluation"""

import time
import uuid
from typing import Any

import mlflow
import numpy as np
import pandas as pd
from prefect import flow, task

from ..adapters import SklearnAdapter, SklearnParallelAdapter
from ..config import settings
from ..evaluation import ExperimentEvaluator, PerformanceMetrics, QualityMetrics
from ..pipelines import DataLoader, TaxiTripPreprocessor
from ..storage import PostgresClient


@task(name="load_and_prepare_data")
def load_and_prepare_data_task(
    data_source: str,
    coordinate_type: str = "pickup",
    use_location_ids: bool = True,
    max_samples: int | None = None,
    use_minio: bool = True,
) -> tuple[pd.DataFrame, np.ndarray]:
    """
    Load and prepare data for evaluation

    Args:
        data_source: Object name in MinIO or local file path
        coordinate_type: Type of coordinates to extract
        use_location_ids: Use location IDs if coordinates not available
        max_samples: Maximum number of samples
        use_minio: If True, load from MinIO first (default: True)

    Returns:
        Tuple of (DataFrame, feature array)
    """
    df = DataLoader.load_data(data_source) if use_minio else DataLoader.load_from_file(data_source)
    if max_samples is not None and len(df) > max_samples:
        df = df.sample(max_samples, random_state=42)

    coords = TaxiTripPreprocessor.extract_coordinates(
        df, coordinate_type=coordinate_type, use_location_ids=use_location_ids
    )
    coords, _ = TaxiTripPreprocessor.filter_valid_coordinates(coords)

    return df, coords


@task(name="run_experiment_with_metrics")
def run_experiment_with_metrics_task(
    adapter_type: str,
    X: np.ndarray,
    eps: float,
    min_samples: int,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Run experiment and collect both performance and quality metrics

    Args:
        adapter_type: Type of adapter
        X: Feature array
        eps: DBSCAN eps parameter
        min_samples: DBSCAN min_samples parameter
        **kwargs: Additional adapter parameters

    Returns:
        Dictionary with experiment results and metrics
    """
    # Initialize adapter
    if adapter_type == "sklearn":
        adapter = SklearnAdapter(**kwargs)
    elif adapter_type == "sklearn_parallel":
        n_jobs = kwargs.pop("n_jobs", -1)
        adapter = SklearnParallelAdapter(n_jobs=n_jobs, **kwargs)
    else:
        raise ValueError(f"Unknown adapter type: {adapter_type}")

    # Run with performance measurement
    def run_clustering():
        return adapter.fit_predict(X, eps=eps, min_samples=min_samples)

    labels, perf_metrics = PerformanceMetrics.measure_with_resources(run_clustering)

    # Compute quality metrics
    quality_metrics = QualityMetrics.compute_all_quality_metrics(X, labels)

    return {
        "labels": labels,
        "performance": perf_metrics,
        "quality": quality_metrics,
        "parameters": {
            "eps": eps,
            "min_samples": min_samples,
            **adapter.get_params(),
        },
        "metadata": adapter.get_metadata(),
    }


@task(name="evaluate_experiment")
def evaluate_experiment_task(
    X: np.ndarray, result: dict[str, Any]
) -> dict[str, Any]:
    """
    Evaluate experiment results

    Args:
        X: Feature array
        result: Experiment result dictionary

    Returns:
        Complete evaluation dictionary
    """
    evaluator = ExperimentEvaluator()
    evaluation = evaluator.evaluate_experiment(
        X, result["labels"], result["performance"]
    )
    evaluation["parameters"] = result["parameters"]
    evaluation["metadata"] = result["metadata"]
    return evaluation


@task(name="log_evaluation_to_mlflow")
def log_evaluation_to_mlflow_task(
    evaluation: dict[str, Any],
    experiment_id: str,
    adapter_type: str,
) -> None:
    """
    Log evaluation results to MLflow

    Args:
        evaluation: Evaluation dictionary
        experiment_id: Experiment ID
        adapter_type: Adapter type
    """
    import os

    # Set AWS credentials
    os.environ["AWS_ACCESS_KEY_ID"] = settings.aws_access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = settings.aws_secret_access_key
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = settings.mlflow_s3_endpoint_url

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.experiment_name)

    with mlflow.start_run(run_name=f"{adapter_type}_{experiment_id}"):
        # Log parameters
        mlflow.log_params(evaluation.get("parameters", {}))

        # Log quality metrics
        quality = evaluation.get("quality", {})
        mlflow.log_metrics(
            {
                "silhouette_score": quality.get("silhouette_score", -1),
                "davies_bouldin_score": quality.get("davies_bouldin_score", float("inf")),
                "calinski_harabasz_score": quality.get("calinski_harabasz_score", 0),
                "n_clusters": quality.get("n_clusters", 0),
                "noise_ratio": quality.get("noise_ratio", 0),
            }
        )

        # Log performance metrics
        performance = evaluation.get("performance", {})
        mlflow.log_metrics(
            {
                "runtime_seconds": performance.get("elapsed_time_seconds", 0),
                "memory_delta_mb": performance.get("memory_delta_mb", 0),
                "cpu_percent": performance.get("cpu_percent", 0),
            }
        )

        # Log overall score
        mlflow.log_metric("overall_score", evaluation.get("overall_score", 0))


@flow(name="evaluation_pipeline", log_prints=True)
def evaluation_pipeline(
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
    Complete evaluation pipeline

    Args:
        data_source: Object name in MinIO or local file path
        adapter_type: Type of adapter
        eps: DBSCAN eps parameter
        min_samples: DBSCAN min_samples parameter
        coordinate_type: Type of coordinates to extract
        use_location_ids: Use location IDs if coordinates not available
        max_samples: Maximum number of samples
        use_minio: If True, load from MinIO first (default: True)
        experiment_id: Experiment ID
        **kwargs: Additional adapter parameters

    Returns:
        Evaluation results dictionary
    """
    if experiment_id is None:
        experiment_id = str(uuid.uuid4())

    # Load and prepare data
    df, X = load_and_prepare_data_task(
        data_source, coordinate_type, use_location_ids, max_samples, use_minio
    )

    # Run experiment with metrics
    result = run_experiment_with_metrics_task(
        adapter_type, X, eps, min_samples, **kwargs
    )

    # Evaluate
    evaluation = evaluate_experiment_task(X, result)
    evaluation["experiment_id"] = experiment_id
    evaluation["adapter_type"] = adapter_type

    # Log to MLflow
    log_evaluation_to_mlflow_task(evaluation, experiment_id, adapter_type)

    return evaluation

