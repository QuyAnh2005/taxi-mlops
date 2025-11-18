"""Parameter sweep workflow for DBSCAN experiments"""

import uuid
from typing import Any

import mlflow
from prefect import flow, task

from ..config import settings
from ..evaluation import ExperimentEvaluator, StatisticalAnalyzer
from .evaluation_flows import evaluation_pipeline


@task(name="run_single_parameter_experiment")
def run_single_parameter_experiment_task(
    data_source: str,
    adapter_type: str,
    eps: float,
    min_samples: int,
    coordinate_type: str,
    use_location_ids: bool,
    max_samples: int | None,
    use_minio: bool,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Run a single experiment with specific parameters

    Args:
        data_source: Object name in MinIO or local file path
        adapter_type: Type of adapter
        eps: DBSCAN eps parameter
        min_samples: DBSCAN min_samples parameter
        coordinate_type: Type of coordinates
        use_location_ids: Use location IDs
        max_samples: Maximum samples
        use_minio: If True, load from MinIO first
        **kwargs: Additional parameters

    Returns:
        Evaluation results
    """
    return evaluation_pipeline(
        data_source=data_source,
        adapter_type=adapter_type,
        eps=eps,
        min_samples=min_samples,
        coordinate_type=coordinate_type,
        use_location_ids=use_location_ids,
        max_samples=max_samples,
        use_minio=use_minio,
        **kwargs,
    )


@flow(name="parameter_sweep", log_prints=True)
def parameter_sweep_flow(
    data_source: str,
    adapter_type: str = "sklearn",
    eps_values: list[float] | None = None,
    min_samples_values: list[int] | None = None,
    coordinate_type: str = "pickup",
    use_location_ids: bool = True,
    max_samples: int | None = None,
    use_minio: bool = True,
    metric: str = "overall_score",
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Perform parameter sweep over eps and min_samples

    Args:
        data_source: Object name in MinIO or local file path
        adapter_type: Type of adapter
        eps_values: List of eps values to test
        min_samples_values: List of min_samples values to test
        coordinate_type: Type of coordinates
        use_location_ids: Use location IDs
        max_samples: Maximum samples
        use_minio: If True, load from MinIO first (default: True)
        metric: Metric to optimize ('overall_score', 'silhouette_score', 'runtime_seconds')
        **kwargs: Additional adapter parameters

    Returns:
        Dictionary with sweep results and best parameters
    """
    if eps_values is None:
        eps_values = [0.1, 0.3, 0.5, 0.7, 1.0]
    if min_samples_values is None:
        min_samples_values = [3, 5, 10, 15]

    sweep_id = str(uuid.uuid4())
    results = []

    # Run experiments for all parameter combinations
    for eps in eps_values:
        for min_samples in min_samples_values:
            print(f"Running experiment: eps={eps}, min_samples={min_samples}")

            evaluation = run_single_parameter_experiment_task(
                data_source=data_source,
                adapter_type=adapter_type,
                eps=eps,
                min_samples=min_samples,
                coordinate_type=coordinate_type,
                use_location_ids=use_location_ids,
                max_samples=max_samples,
                use_minio=use_minio,
                **kwargs,
            )

            # Extract metric value
            if metric == "overall_score":
                metric_value = evaluation.get("overall_score", 0)
            elif metric == "silhouette_score":
                metric_value = evaluation.get("quality", {}).get("silhouette_score", -1)
            elif metric == "runtime_seconds":
                metric_value = evaluation.get("performance", {}).get(
                    "elapsed_time_seconds", 0
                )
            else:
                metric_value = evaluation.get("overall_score", 0)

            results.append(
                {
                    "eps": eps,
                    "min_samples": min_samples,
                    "evaluation": evaluation,
                    "metric_value": metric_value,
                }
            )

    # Find best parameters
    best_result = max(results, key=lambda x: x["metric_value"])

    # Analyze parameter sweep
    eps_values_tested = [r["eps"] for r in results]
    metric_values = [r["metric_value"] for r in results]

    sweep_analysis = StatisticalAnalyzer.analyze_parameter_sweep(
        eps_values_tested, metric_values, "eps"
    )

    return {
        "sweep_id": sweep_id,
        "adapter_type": adapter_type,
        "num_experiments": len(results),
        "results": results,
        "best_parameters": {
            "eps": best_result["eps"],
            "min_samples": best_result["min_samples"],
            "metric_value": best_result["metric_value"],
        },
        "sweep_analysis": sweep_analysis,
    }


@flow(name="compare_adapters_sweep", log_prints=True)
def compare_adapters_sweep_flow(
    data_source: str,
    eps_values: list[float] | None = None,
    min_samples_values: list[int] | None = None,
    coordinate_type: str = "pickup",
    use_location_ids: bool = True,
    max_samples: int | None = None,
    use_minio: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Compare both adapters with parameter sweep

    Args:
        data_source: Object name in MinIO or local file path
        eps_values: List of eps values
        min_samples_values: List of min_samples values
        coordinate_type: Type of coordinates
        use_location_ids: Use location IDs
        max_samples: Maximum samples
        use_minio: If True, load from MinIO first (default: True)
        **kwargs: Additional parameters

    Returns:
        Comparison results
    """
    # Run sweep for sequential adapter
    print("Running parameter sweep for sequential adapter...")
    sequential_sweep = parameter_sweep_flow(
        data_source=data_source,
        adapter_type="sklearn",
        eps_values=eps_values,
        min_samples_values=min_samples_values,
        coordinate_type=coordinate_type,
        use_location_ids=use_location_ids,
        max_samples=max_samples,
        use_minio=use_minio,
        **kwargs,
    )

    # Run sweep for parallel adapter
    print("Running parameter sweep for parallel adapter...")
    parallel_sweep = parameter_sweep_flow(
        data_source=data_source,
        adapter_type="sklearn_parallel",
        eps_values=eps_values,
        min_samples_values=min_samples_values,
        coordinate_type=coordinate_type,
        use_location_ids=use_location_ids,
        max_samples=max_samples,
        use_minio=use_minio,
        **kwargs,
    )

    # Compare results
    evaluator = ExperimentEvaluator()

    # Compare best results
    seq_best = sequential_sweep["best_parameters"]
    par_best = parallel_sweep["best_parameters"]

    return {
        "sequential_sweep": sequential_sweep,
        "parallel_sweep": parallel_sweep,
        "comparison": {
            "best_sequential": seq_best,
            "best_parallel": par_best,
            "runtime_comparison": {
                "sequential_best_runtime": sequential_sweep["results"][0]["evaluation"]
                .get("performance", {})
                .get("elapsed_time_seconds", 0),
                "parallel_best_runtime": parallel_sweep["results"][0]["evaluation"]
                .get("performance", {})
                .get("elapsed_time_seconds", 0),
            },
        },
    }

