"""Scheduled workflows using Prefect

Note: In Prefect 2.x, schedules are configured during deployment, not in the flow decorator.
To schedule these flows, use:
    prefect deploy src/workflows/scheduled_workflows.py:daily_adapter_comparison_flow --cron "0 2 * * *"
    prefect deploy src/workflows/scheduled_workflows.py:weekly_parameter_sweep_flow --cron "0 3 * * 1"
"""

from datetime import datetime, timedelta
from typing import Any

from prefect import flow

from ..config import settings
from ..evaluation import ExperimentEvaluator, StatisticalAnalyzer
from .parameter_sweep import compare_adapters_sweep_flow


@flow(
    name="daily_adapter_comparison",
    log_prints=True,
)
def daily_adapter_comparison_flow(
    data_source: str = "yellow_tripdata_2025-09.parquet",
    max_samples: int = 10000,
    use_minio: bool = True,
) -> dict[str, Any]:
    """
    Daily scheduled comparison of sequential vs parallel adapters

    Schedule: Run daily at 2 AM UTC
    Deploy with: prefect deploy src/workflows/scheduled_workflows.py:daily_adapter_comparison_flow --cron "0 2 * * *"

    Args:
        data_source: Object name in MinIO or local file path
        max_samples: Maximum number of samples
        use_minio: If True, load from MinIO first (default: True)

    Returns:
        Comparison results
    """
    print(f"Running daily comparison at {datetime.now()}")

    # Run comparison with default parameters
    return compare_adapters_sweep_flow(
        data_source=data_source,
        eps_values=[0.3, 0.5, 0.7],
        min_samples_values=[5, 10],
        max_samples=max_samples,
        use_minio=use_minio,
    )


@flow(
    name="weekly_parameter_sweep",
    log_prints=True,
)
def weekly_parameter_sweep_flow(
    data_source: str = "yellow_tripdata_2025-09.parquet",
    max_samples: int = 50000,
    use_minio: bool = True,
) -> dict[str, Any]:
    """
    Weekly scheduled comprehensive parameter sweep

    Schedule: Run weekly on Mondays at 3 AM UTC
    Deploy with: prefect deploy src/workflows/scheduled_workflows.py:weekly_parameter_sweep_flow --cron "0 3 * * 1"

    Args:
        data_source: Object name in MinIO or local file path
        max_samples: Maximum number of samples
        use_minio: If True, load from MinIO first (default: True)

    Returns:
        Sweep results
    """
    print(f"Running weekly parameter sweep at {datetime.now()}")

    from .parameter_sweep import parameter_sweep_flow

    return parameter_sweep_flow(
        data_source=data_source,
        adapter_type="sklearn",
        eps_values=[0.1, 0.3, 0.5, 0.7, 1.0, 1.5],
        min_samples_values=[3, 5, 10, 15, 20],
        max_samples=max_samples,
        use_minio=use_minio,
    )


@flow(name="aggregate_results", log_prints=True)
def aggregate_results_flow(
    adapter_type: str | None = None,
    days: int = 7,
) -> dict[str, Any]:
    """
    Aggregate and analyze results from recent experiments

    Args:
        adapter_type: Filter by adapter type (None = all)
        days: Number of days to look back

    Returns:
        Aggregated analysis results
    """
    from datetime import timedelta

    from ..storage import PostgresClient

    print(f"Aggregating results from last {days} days")

    postgres_client = PostgresClient()

    # Get experiments from database
    if adapter_type:
        experiments = postgres_client.list_experiments(adapter_type=adapter_type)
    else:
        experiments = postgres_client.list_experiments()

    if not experiments:
        return {"message": "No experiments found", "experiments": []}

    # Filter by date (if created_at is available)
    # For now, use all experiments

    # Extract metrics
    evaluator = ExperimentEvaluator()
    evaluations = []

    for exp in experiments:
        metrics = exp.get("metrics", {})
        quality = {
            "silhouette_score": metrics.get("silhouette_score", -1),
            "davies_bouldin_score": metrics.get("davies_bouldin_score", float("inf")),
            "n_clusters": metrics.get("n_clusters", 0),
            "noise_ratio": metrics.get("noise_ratio", 0),
        }
        performance = {
            "elapsed_time_seconds": metrics.get("elapsed_time_seconds", 0),
        }
        evaluations.append(
            {
                "quality": quality,
                "performance": performance,
                "overall_score": metrics.get("overall_score", 0),
            }
        )

    # Aggregate
    aggregated = evaluator.aggregate_evaluations(evaluations)

    # Statistical analysis
    silhouette_scores = [
        e["quality"]["silhouette_score"] for e in evaluations if e["quality"]["silhouette_score"] >= -1
    ]
    runtimes = [e["performance"]["elapsed_time_seconds"] for e in evaluations]

    analysis = {
        "silhouette_stats": StatisticalAnalyzer.compute_summary_statistics(
            silhouette_scores
        ),
        "runtime_stats": StatisticalAnalyzer.compute_summary_statistics(runtimes),
    }

    return {
        "num_experiments": len(experiments),
        "aggregated_metrics": aggregated,
        "statistical_analysis": analysis,
        "experiments": experiments[:10],  # Return first 10 for reference
    }

